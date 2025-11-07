import aws_cdk as cdk
from typing import Dict
from aws_cdk import (
    aws_ec2 as _ec2,
    aws_efs as _efs,
    aws_ecs as _ecs,
    aws_backup as _backup,
    aws_iam as _iam,
    aws_kms as _kms,
    aws_events as _events,
    RemovalPolicy,
    Tags,
)

from constructs import Construct


class EFSVolume(Construct):
    """

    The FAO CDK EDS Construct creates AWS Elastic File Systems (AWS EFS) resources.

    The construct automatically enables the following main features:

    -	Conditionally configure the volume removal policy depending on the environment in which the construct is deployed. The policy will be set as `RETAIN` for the Production environment, otherwise set to `DESTROY`;
    -	Integration with FAO backups and restore tools for volumes deployed on the Production environment (AWS Backup);
    -	AWS Backup setup when deployed on the Production environment and configured backup plan according to FAO standards;
    -	Retain the AWS Backup vault when deployed on the Production environment;

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:
        scope (Construct): Parent construct

        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliance. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        vpc (aws_ec2.IVpc): VPC where the cluster will be attached to.

        volume_mount_path (str): path where the volume will be mounted in the container

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        to_be_backed_up (bool): Flag to tag the resource to be backed up. Default: True (only works if the environment is production)

        efs_backup (bool): EFS backed up using AWS Backup Default: True

        omit_cloudformation_template_outputs(bool): Omit the generation of CloudFormation template outputs. Default: false

    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name,
        vpc: _ec2.IVpc,
        environment: str,
        environments_parameters: Dict,
        to_be_backed_up: bool = True,
        aws_back_up: bool = True,
        volume_mount_path: str = '',
        omit_cloudformation_template_outputs: bool = False,
    ):
        self.scope = scope
        self.id = id
        self.vpc = vpc
        self.volume_mount_path = volume_mount_path
        self._environments_parameters = environments_parameters
        self._environment = environment
        self.app_name = app_name

        super().__init__(scope, id)

        efs_removal_policy = RemovalPolicy.DESTROY
        if environment.lower() == 'production':
            efs_removal_policy = RemovalPolicy.RETAIN
        elif to_be_backed_up:
            to_be_backed_up = False  # if the environment is not production, the EFS cannot be backed up

        if self.id.split('-')[-1] == 'efsvolumefromms':
            # Call from aws-cdk-constructs/ecs/microservice.py we need to maintain backwards compatibility
            fs_name = '-'.join(self.id.split('-')[:-1])
            fs_name = fs_name + 'efs'
        else:
            fs_name = self.id + '-efs'

        self.efs = _efs.FileSystem(
            scope=self.scope,
            id=fs_name,  # EFS name to maintain compatibility with the old naming convention
            vpc=vpc,
            encrypted=False,
            removal_policy=efs_removal_policy,
        )

        self._efs_security_group = self.efs.node.find_child('EfsSecurityGroup')

        if to_be_backed_up:
            Tags.of(self.efs).add('HasBackup', 'true')
        else:
            Tags.of(self.efs).add('HasBackup', 'false')

        self.efs_volume_configuration = _ecs.EfsVolumeConfiguration(
            file_system_id=self.efs.file_system_id,
        )

        if aws_back_up:
            # KMS Vault Encryption key
            aws_account = environments_parameters['accounts'][
                environment.lower()
            ]
            account_id = aws_account['id']
            key_arn = (
                'arn:aws:kms:eu-west-1:'
                + account_id
                + ':key/'
                + aws_account['kms_vault_key']
            )

            # Create AWS Backup Role

            backup_role = self._get_backup_role()

            # Inline policies
            backup_role.attach_inline_policy(
                _iam.Policy(
                    self,
                    'backup_and_restore_policies',
                    statements=[
                        # Policy for Vault
                        _iam.PolicyStatement(
                            actions=['backup:DescribeBackupVault'],
                            resources=['arn:aws:backup:*:*:backup-vault:*'],
                        ),
                        _iam.PolicyStatement(
                            actions=[
                                'backup:CopyIntoBackupVault',
                                'backup:CopyFromBackupVault',
                            ],
                            resources=[
                                'arn:aws:backup:*:*:backup-vault:*'
                                + app_name
                                + '*'
                            ],
                        ),
                        # Policy for EFS
                        _iam.PolicyStatement(
                            actions=[
                                'elasticfilesystem:DescribeTags',
                                'elasticfilesystem:Backup',
                                'elasticfilesystem:Restore',
                            ],
                            resources=[
                                'arn:aws:elasticfilesystem:*:*:file-system/'
                                + self.efs.file_system_id
                            ],
                        ),
                        _iam.PolicyStatement(
                            actions=['elasticfilesystem:DescribeFilesystems'],
                            resources=[
                                'arn:aws:elasticfilesystem:*:*:file-system/*'
                            ],
                        ),
                        # Policy for Tags
                        _iam.PolicyStatement(
                            actions=['tag:GetResources'],
                            resources=['*'],
                        ),
                    ],
                )
            )

            # Create AWS Backup Vault

            backup_vault = self._get_backup_vault(key_arn=key_arn)

            # Create AWS Backup Plans

            # Backup Plan
            backup_plan = self._get_backup_plan(backup_vault=backup_vault)
            backup_plan.add_selection(
                id=f'{self.app_name}_{self.id}',
                resources=[
                    _backup.BackupResource.from_efs_file_system(self.efs)
                ],
                backup_selection_name=f'{self.app_name}_{self.id}_backup_selection',
                role=backup_role,
            )

    def _get_backup_vault(self, key_arn: str) -> _backup.BackupVault:
        path = '_'.join(self.node.path.split('/')[:-1])
        return self.scope.node.try_find_child(
            f'{path}-vault'
        ) or self._create_backup_vault(key_arn=key_arn)

    def _create_backup_vault(self, key_arn: str) -> _backup.BackupVault:
        path = '_'.join(self.node.path.split('/')[:-1])
        vault_removal_policy = RemovalPolicy.DESTROY
        if self._environment.lower() == 'production':
            vault_removal_policy = RemovalPolicy.RETAIN
        vault_encryption_key = _kms.Key.from_key_arn(
            self, id=self.app_name + 'vault_key', key_arn=key_arn
        )
        return _backup.BackupVault(
            scope=self.scope,
            id=f'{path}-vault',
            backup_vault_name=path + '-' + 'Vault',
            encryption_key=vault_encryption_key,
            removal_policy=vault_removal_policy,
        )

    def _get_backup_role(self) -> _iam.Role:
        return (
            self.scope.node.try_find_child('aws_backup_role')
            or self._create_backup_role()
        )

    def _create_backup_role(self) -> _iam.Role:
        return _iam.Role(
            self.scope,
            id=f'aws_backup_role',
            description=self.app_name + '_' + 'aws_backup_role',
            assumed_by=_iam.ServicePrincipal('backup.amazonaws.com'),
            # role_name=self.app_name + "_" + "aws_backup_role", # Do not include role name to avoid conflicts in case of refactoring
        )

    def _get_backup_plan(
        self, backup_vault: _backup.BackupVault
    ) -> _backup.BackupPlan:
        path = '_'.join(self.node.path.split('/')[:-1])
        return self.scope.node.try_find_child(
            f'{path}_BackupPlan'
        ) or self._create_backup_plan(backup_vault=backup_vault)

    def _create_backup_plan(
        self, backup_vault: _backup.BackupVault
    ) -> _backup.BackupPlan:
        path = '_'.join(self.node.path.split('/')[:-1])
        return _backup.BackupPlan(
            self.scope,
            id=f'{path}_BackupPlan',
            backup_vault=backup_vault,
            backup_plan_rules=(
                [
                    (
                        _backup.BackupPlanRule(
                            backup_vault=backup_vault,
                            delete_after=cdk.Duration.days(35),
                            rule_name=self.app_name + '_' + 'DailyPlan',
                            schedule_expression=_events.Schedule.cron(
                                day='*', hour='20', minute='00'
                            ),
                        )
                    ),
                    (
                        _backup.BackupPlanRule(
                            backup_vault=backup_vault,
                            delete_after=cdk.Duration.days(366),
                            rule_name=self.app_name + '_' + 'MonthlyPlan',
                            schedule_expression=_events.Schedule.cron(
                                hour='20',
                                minute='30',
                                day='L',
                                month='*',
                                year='*',
                            ),
                            move_to_cold_storage_after=cdk.Duration.days(35),
                        )
                    ),
                ]
            ),
        )

    def get_file_system(self) -> _efs.FileSystem:
        """Get the EFS file system"""
        return self.efs

    def grant_access(self, peer: _ec2.SecurityGroup) -> None:
        """
        Grant access to the EFS volume to a security group
        :param peer:
        """
        self._efs_security_group.add_ingress_rule(
            peer=peer,
            connection=_ec2.Port.tcp(2049),
            description='Allow EFS access to NFS',
        )

    def get_mount_point(self) -> _ecs.MountPoint:
        """Get the mount point for the EFS volume"""
        return _ecs.MountPoint(
            source_volume=self.id,
            read_only=False,
            container_path=self.volume_mount_path,
        )
