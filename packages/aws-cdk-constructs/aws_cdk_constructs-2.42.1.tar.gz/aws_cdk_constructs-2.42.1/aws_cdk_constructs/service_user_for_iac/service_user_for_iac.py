import aws_cdk as cdk
from aws_cdk import aws_iam as _iam, Tags
from constructs import Construct

from aws_cdk_constructs.utils import (
    normalize_environment_parameter,
    get_version,
)


class ServiceUserForIAC(Construct):
    """
    The FAO CDK ServiceUserForIAC Construct creates an AWS IAM user with permission to deploy a whole infrastructure. The permissions are defined according to the least privileges principle leveraging AWS Tags and resources ARNs filtering.

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:
        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        s3_assets_bucket_name (str): The S3 Bucket in which the application assets are stored

        s3_code_bucket_name (str): The S3 Bucket in which the application code-base is stored

        repo_name (str): The name of the GitHub repository to which the user will have access from GitHub Actions, defining this parameter will create the GitHub Actions role for the user. It can be multiple repo name divided by a pipe "|"

    """

    @property
    def service_user(self) -> _iam.User:
        """Returns the Service User object

        Returns:
            aws_cdk.aws_iam.User: The Service User object
        """
        return self._service_user

    @property
    def service_role(self) -> _iam.Role:
        """Returns the Service Role object

        Returns:
            aws_cdk.aws_iam.Role: The Service Role object
        """
        return self._service_role

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name: str,
        environment: str,
        environments_parameters: dict,
        s3_code_bucket_name: str = None,
        s3_assets_bucket_name: str = None,
        repo_name: str = None,
        **kwargs,
    ) -> None:

        repos_name = (
            repo_name.replace(' ', '').split('|') if repo_name else None
        )
        super().__init__(scope, id, **kwargs)
        environment = normalize_environment_parameter(environment)
        is_production = environment == 'Production'

        # Apply mandatory tags
        cdk.Tags.of(self).add('ApplicationName', app_name.lower().strip())
        cdk.Tags.of(self).add('Environment', environment)

        # Apply FAO CDK tags
        cdk.Tags.of(self).add('fao-cdk-construct', 'service_user_for_iac')
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk-version', get_version())
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk', 'true')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create conditions

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validate input params

        aws_account = environments_parameters['accounts'][environment.lower()]
        common_parameters = environments_parameters['common']

        account_id = aws_account['id']

        kms_ssm_key = aws_account['kms_ssm_key']
        kms_rds_key = aws_account['kms_rds_key']
        kms_ebs_key = aws_account['kms_ebs_key']
        kms_vault_key = aws_account['kms_vault_key']
        kms_fao_cdk_ami_al2_key_arn = common_parameters[
            'kms_fao_cdk_ami_al2_key_arn'
        ]
        kms_fao_cdk_ami_al2023_key_arn = common_parameters[
            'kms_fao_cdk_ami_al2023_key_arn'
        ]

        # S3 buckets
        s3_buckets = [
            f'arn:aws:s3:::{app_name}*',
            f'arn:aws:s3:::{app_name.replace("-", "")}*',
            f'arn:aws:s3:::{app_name.replace("-", ".")}*',
            'arn:aws:s3:::awsserverlessrepo-changesets-*',
            'arn:aws:s3:::cdktoolkit*',
            'arn:aws:s3:::cdk-*',
        ]

        if s3_code_bucket_name is not None:
            s3_buckets.append(f'arn:aws:s3:::{s3_code_bucket_name}*')

        if s3_assets_bucket_name is not None:
            s3_buckets.append(f'arn:aws:s3:::{s3_assets_bucket_name}*')
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Retrieve info from already existing AWS resources
        # Important: you need an internet connection!

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create AWS resources

        # Manage policy for IAC deployment
        managed_policy_for_iac_1 = _iam.ManagedPolicy(
            self,
            'managed_policy_iac_one',
            description=app_name + ' managed policy for IAC',
            statements=[
                # Resource ALL
                _iam.PolicyStatement(
                    actions=[
                        'backup:CreateBackupPlan',
                        'backup:CreateBackupSelection',
                        'backup:DescribeBackupVault',
                        'backup:CreateBackupVault',
                        'cloudformation:Describe*',
                        'cloudformation:ValidateTemplate',
                        'cloudformation:ExecuteChangeSet',
                        'cloudformation:*ChangeSet*',
                        'cloudformation:GetTemplate',
                        'cloudformation:ListStackResources',
                        'ec2:CreateSecurityGroup',
                        'ec2:*SecurityGroup*',
                        'ec2:Describe*',
                        'ec2:*Tag*',
                        'serverlessrepo:SearchApplications',
                        'serverlessrepo:GetApplication',
                        'serverlessrepo:*CloudFormationTemplate',
                        'serverlessrepo:*CloudFormationChangeSet',
                        'serverlessrepo:List*',
                        'serverlessrepo:Get*',
                        'secretsmanager:GetRandomPassword',
                        'elasticloadbalancingv2:Describe*',
                        'elasticloadbalancing:Describe*',
                        'elasticloadbalancing:Delete*',
                        'elasticloadbalancingv2:*',
                        'elasticloadbalancing:*',
                        'elasticloadbalancing:ModifyLoadBalancerAttributes*',
                        'autoscaling:Describe*',
                        'iam:PutRolePolicy',
                        'iam:getRolePolicy',
                        'iam:GetUser',
                        'iam:DeleteRolePolicy',
                        'iam:DetachUserPolicy',
                        'iam:ListAccessKeys',
                        'iam:DeleteUser',
                        'iam:AttachUserPolicy',
                        'iam:PassRole',
                        'iam:DeleteAccessKey',
                        'rds:Describe*',
                        'elasticfilesystem:*MountTarget*',
                        'elasticfilesystem:DescribeMountTargets',
                        'elasticfilesystem:DescribeFileSystems',
                        'ec2:*Volume*',
                        'elasticfilesystem:ListTagsForResource',
                        'elasticfilesystem:DescribeFileSystemPolicy',
                        'elasticfilesystem:TagResource',
                        'elasticfilesystem:UntagResource',
                        'autoscaling:DeletePolicy',
                        'cognito-idp:*UserPoolClient',
                        'cloudfront:TagResource',
                        'ecs:Describe*',
                        'ecs:List*',
                        'ecs:Create*',
                        'ecs:DiscoverPollEndpoint',
                        'ecs:TagResource',
                        'iam:ListAttachedRolePolicies',
                        'iam:ListInstanceProfiles',
                        'iam:ListRoles',
                    ],
                    resources=['*'],
                ),
                # Filter by ARN pattern
                _iam.PolicyStatement(
                    actions=[
                        'cloudformation:*',
                    ],
                    resources=[
                        f'arn:aws:cloudformation:*:*:stack/{app_name}*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        's3:*',
                    ],
                    resources=s3_buckets,
                ),
                _iam.PolicyStatement(
                    actions=[
                        'ec2:*',
                    ],
                    resources=[f'arn:aws:ec2:eu-west-1:*:*/{app_name}*'],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'ec2:*',
                    ],
                    resources=['*'],
                    conditions={
                        'ForAnyValue:StringEquals': {
                            'ec2:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'elasticloadbalancingv2:*',
                        'elasticloadbalancing:*',
                    ],
                    resources=[
                        f'arn:aws:elasticloadbalancing:eu-west-1:*:*/{app_name}*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'rds:*',
                    ],
                    resources=[
                        f'arn:aws:rds:eu-west-1:*:*:{app_name}*',
                        'arn:aws:rds:eu-west-1:*:*:*default*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'secretsmanager:*',
                    ],
                    resources=[
                        f'arn:aws:secretsmanager:eu-west-1:*:*:{app_name}*'
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'lambda:*',
                    ],
                    resources=[f'arn:aws:lambda:*:*:*:{app_name}*'],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'autoscaling:*',
                    ],
                    resources=[
                        f'arn:aws:autoscaling:eu-west-1:*:*:*:*{app_name}*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=['apigateway:*'],
                    resources=[
                        f'arn:aws:apigateway:*::/{app_name}*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'elasticfilesystem:*',
                    ],
                    resources=[
                        'arn:aws:elasticfilesystem:eu-west-1:*:*:*:*'
                        + app_name
                        + '*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'iam:*',
                    ],
                    resources=[
                        f'arn:aws:iam::*:user/{app_name}*',
                        # "arn:aws:iam::*:federated-user/" + app_name + "*",
                        f'arn:aws:iam::*:role/{app_name}*',
                        f'arn:aws:iam::*:group/{app_name}*',
                        f'arn:aws:iam::*:instance-profile/{app_name}*',
                        # "arn:aws:iam::*:mfa/" + app_name + "*",
                        # "arn:aws:iam::*:server-certificate/" + app_name + "*",
                        f'arn:aws:iam::*:policy/{app_name}*',
                        # "arn:aws:iam::*:sms-mfa/" + app_name + "*",
                        # "arn:aws:iam::*:saml-provider/" + app_name + "*",
                        # "arn:aws:iam::*:oidc-provider/" + app_name + "*",
                        # "arn:aws:iam::*:report/" + app_name + "*",
                        # "arn:aws:iam::*:access-report/" + app_name + "*",
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'cloudfront:*',
                    ],
                    resources=[
                        f'arn:aws:cloudfront:eu-west-1:*:*:*:*{app_name}*',
                        'arn:aws:cloudfront::*:distribution/*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'kendra:*',
                    ],
                    resources=[
                        f'arn:aws:kendra:eu-west-1:*:*{app_name}*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'cloudwatch:*',
                    ],
                    resources=[
                        f'arn:aws:cloudwatch:*:*:dashboard/{app_name}*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'cloudwatch:*',
                    ],
                    resources=[
                        f'arn:aws:cloudwatch:*:alarm:{app_name}*',
                    ],
                ),
            ],
        )

        managed_policy_for_iac_2 = _iam.ManagedPolicy(
            self,
            'managed_policy_iac_two',
            description=app_name + ' managed policy for IAC 2',
            statements=[
                # Filter by TAG
                _iam.PolicyStatement(
                    actions=[
                        'cloudformation:*',
                        's3:*',
                        'ec2:*',
                        'elasticloadbalancingv2:*',
                        'elasticloadbalancing:*',
                        'rds:*',
                        'secretsmanager:*',
                        'autoscaling:*',
                        'lambda:*',
                        'logs:*',
                        'iam:*',
                        'elasticfilesystem:*',
                        'cloudfront:*',
                        'kendra:*',
                    ],
                    resources=['*'],
                    conditions={
                        'ForAnyValue:StringLike': {
                            'aws:RequestTag/ApplicationName': app_name,
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'cloudformation:*',
                        's3:*',
                        'ec2:*',
                        'elasticloadbalancingv2:*',
                        'elasticloadbalancing:*',
                        'rds:*',
                        'secretsmanager:*',
                        'autoscaling:*',
                        'lambda:*',
                        'logs:*',
                        'iam:*',
                        'elasticfilesystem:*',
                        'cloudfront:*',
                        'kendra:*',
                    ],
                    resources=['*'],
                    conditions={
                        'ForAnyValue:StringLike': {
                            'ec2:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'cloudwatch:*',
                    ],
                    resources=['*'],
                    conditions={
                        'ForAnyValue:StringLike': {
                            'ec2:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'kms:*',
                    ],
                    resources=['*'],
                    conditions={
                        'ForAnyValue:StringLike': {
                            'aws:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'ecs:*',
                    ],
                    resources=['*'],
                    conditions={
                        'StringLike': {
                            'ecs:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'ecr:*',
                    ],
                    resources=['*'],
                    conditions={
                        'StringLike': {
                            'ecr:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                # Relative to ECS
                _iam.PolicyStatement(
                    actions=[
                        'ssm:GetParameter',
                        'ssm:GetParameters',
                        'ssm:GetParametersByPath',
                    ],
                    resources=['arn:aws:ssm:*:*:parameter/aws/service/ecs*'],
                ),
                _iam.PolicyStatement(
                    actions=['iam:PassRole'],
                    resources=['*'],
                    conditions={
                        'StringLike': {
                            'iam:PassedToService': 'ecs-tasks.amazonaws.com'
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'iam:PassRole',
                    ],
                    resources=['arn:aws:iam::*:role/ecsInstanceRole*'],
                    conditions={
                        'StringLike': {
                            'iam:PassedToService': [
                                'ec2.amazonaws.com',
                                'ec2.amazonaws.com.cn',
                            ]
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'iam:PassRole',
                    ],
                    resources=['arn:aws:iam::*:role/ecsAutoscaleRole*'],
                    conditions={
                        'StringLike': {
                            'iam:PassedToService': [
                                'application-autoscaling.amazonaws.com',
                                'application-autoscaling.amazonaws.com.cn',
                            ]
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'iam:CreateServiceLinkedRole',
                    ],
                    resources=['*'],
                    conditions={
                        'StringLike': {
                            'iam:AWSServiceName': [
                                'autoscaling.amazonaws.com',
                                'ecs.amazonaws.com',
                                'ecs.application-autoscaling.amazonaws.com',
                                'spot.amazonaws.com',
                                'spotfleet.amazonaws.com',
                            ]
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=['ecr:*'],
                    resources=[f'arn:aws:ecr:eu-west-1:*:*{app_name}*'],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'ecr:GetAuthorizationToken',
                        'ecr:DescribeRepositories',
                    ],
                    resources=['*'],
                ),
                # Relative to Backup
                _iam.PolicyStatement(
                    actions=[
                        'backup:DeleteBackupPlan',
                        'backup:DeleteBackupSelection',
                        'backup:DeleteBackupVault',
                    ],
                    resources=['*'],
                    conditions={
                        'ForAnyValue:StringLike': {
                            'ec2:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=[
                        'backup:DeleteBackupPlan',
                        'backup:DeleteBackupSelection',
                        'backup:DeleteBackupVault',
                    ],
                    resources=['*'],
                    conditions={
                        'ForAnyValue:StringLike': {
                            'aws:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
                _iam.PolicyStatement(
                    actions=['backup:DeleteBackupVault'],
                    resources=[
                        f'arn:aws:backup:eu-west-1:*:backup-vault:{app_name}*'
                    ],
                ),
                # Filter by SPECIFIC RESOURCE
                _iam.PolicyStatement(
                    actions=[
                        'kms:Decrypt',
                        'kms:Encrypt',
                        'kms:ReEncrypt*',
                        'kms:GenerateDataKey*',
                        'kms:Describe*',
                        'kms:CreateGrant',
                        'kms:DescribeKey',
                    ],
                    resources=[
                        f'arn:aws:kms:eu-west-1:{account_id}:key/{kms_ebs_key}',
                        f'arn:aws:kms:eu-west-1:{account_id}:key/{kms_rds_key}',
                        f'arn:aws:kms:eu-west-1:{account_id}:key/{kms_ssm_key}',
                        f'arn:aws:kms:eu-west-1:{account_id}:key/{kms_vault_key}',
                        kms_fao_cdk_ami_al2_key_arn,
                        kms_fao_cdk_ami_al2023_key_arn,
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'ssm:Describe*',
                        'ssm:Get*',
                        'ssm:List*',
                        'ssm:Put*',
                        'ssm:AddTags*',
                    ],
                    resources=[
                        f'arn:aws:ssm:*:*:parameter/*{app_name}*',
                        f'arn:aws:ssm:*:{account_id}:parameter/common/*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=['apigateway:*'],
                    resources=[
                        '*',
                    ],
                    conditions={
                        'ForAnyValue:StringEquals': {
                            'aws:ResourceTag/ApplicationName': app_name
                        }
                    },
                ),
            ],
        )

        # Managed policy for Configuration deployment
        managed_policy_for_static_assets = _iam.ManagedPolicy(
            self,
            'service_user_policies',
            statements=[
                # S3 Configuration bucket permissions
                _iam.PolicyStatement(
                    actions=['s3:*'],
                    resources=[
                        f'arn:aws:s3:::{aws_account["s3_config_bucket"]}/{app_name}/{environment}/',
                        f'arn:aws:s3:::{aws_account["s3_config_bucket"]}/{app_name}/{environment}/*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=['s3:ListBucket*'],
                    resources=[
                        f'arn:aws:s3:::{aws_account["s3_config_bucket"]}'
                    ],
                ),
            ],
        )

        if not is_production:
            # Route53 records
            dns_statement = _iam.PolicyStatement(
                actions=[
                    'route53:ChangeResourceRecordSets',
                    'route53:GetHostedZone*',
                    'route53:ListHostedZones*',
                ],
                resources=['*'],
            )
            managed_policy_for_iac_2.add_statements(dns_statement)

        # Managed policy for Configuration deployment
        managed_policy_for_cdk = _iam.ManagedPolicy(
            self,
            'service_user_policy_cdk',
            statements=[
                _iam.PolicyStatement(
                    actions=[
                        'ssm:Describe*',
                        'ssm:Get*',
                        'ssm:List*',
                    ],
                    resources=[
                        'arn:aws:ssm:*:*:*cdk*',
                        'arn:aws:ssm:*:*:parameter/cdk*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'ecr:*',
                    ],
                    resources=['arn:aws:ecr:*:*:repository/*cdk*'],
                ),
            ],
        )

        # Service user
        self._service_user = _iam.User(
            self,
            'service_user',
            managed_policies=[
                managed_policy_for_iac_1,
                managed_policy_for_iac_2,
                managed_policy_for_static_assets,
                managed_policy_for_cdk,
            ],
            user_name=f'SRVUSR-{app_name}_{environment}_iac',
        )
        if repos_name:
            Tags.of(self._service_user).add('GHA_ROLE', 'True')
            id = (
                environments_parameters.get('accounts')
                .get(environment.lower())
                .get('id')
            )
            self.principal = _iam.FederatedPrincipal(
                federated=f'arn:aws:iam::{id}:oidc-provider/token.actions.githubusercontent.com',
                conditions={
                    'StringEquals': {
                        'token.actions.githubusercontent.com:aud': 'sts.amazonaws.com',
                    },
                    'StringLike': {
                        'token.actions.githubusercontent.com:sub': [
                            f'repo:un-fao/{x}:*' for x in repos_name
                        ]
                    },
                },
                assume_role_action='sts:AssumeRoleWithWebIdentity',
            )

            self._service_role = _iam.Role(
                role_name=f'SRVROLE-{app_name}_{environment.lower()}_iac',
                scope=self,
                id='service_role',
                assumed_by=self.principal,
                managed_policies=[
                    managed_policy_for_iac_1,
                    managed_policy_for_iac_2,
                    managed_policy_for_static_assets,
                    managed_policy_for_cdk,
                ],
            )

        # S3 Code bucket permissions
        if s3_code_bucket_name:
            s3_code_bucket_policy = _iam.ManagedPolicy(
                self,
                'service_user_s3_code_bucket_policies',
                statements=[
                    # S3 Assets bucket permissions
                    _iam.PolicyStatement(
                        actions=['s3:*'],
                        resources=[
                            f'arn:aws:s3:::{s3_code_bucket_name}',
                            f'arn:aws:s3:::{s3_code_bucket_name}/*',
                        ],
                    ),
                ],
            )
            self._service_user.add_managed_policy(s3_code_bucket_policy)
            if repos_name:
                self._service_role.add_managed_policy(s3_code_bucket_policy)

            # S3 Assets bucket permissions
        # S3 Assets bucket permissions
        if s3_assets_bucket_name:
            s3_assets_bucket_policy = _iam.ManagedPolicy(
                self,
                'service_user_s3_assets_bucket_policies',
                statements=[
                    _iam.PolicyStatement(
                        actions=['s3:*'],
                        resources=[
                            f'arn:aws:s3:::{s3_assets_bucket_name}',
                            f'arn:aws:s3:::{s3_assets_bucket_name}/*',
                        ],
                    ),
                ],
            )
            self._service_user.add_managed_policy(s3_assets_bucket_policy)
            if repos_name:
                self._service_role.add_managed_policy(s3_assets_bucket_policy)
