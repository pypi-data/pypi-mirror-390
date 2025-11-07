import aws_cdk as cdk
import aws_cdk.aws_s3
from constructs import Construct
from aws_cdk import (
    aws_rds as _rds,
    aws_ec2 as _ec2,
    aws_cloudwatch as _cloudwatch,
    aws_docdb as _docdb,
    aws_neptune_alpha as _neptune,
)
from aws_cdk_constructs.utils import (
    normalize_environment_parameter,
    get_version,
)
from aws_cdk_constructs.database._types.relational import RelationalDatabase
from aws_cdk_constructs.database._types.graph import GraphDatabase
from aws_cdk_constructs.database.types import DatabaseType
from aws_cdk_constructs.database._types.document import DocumentDatabase

from typing import Union, List


class Database(Construct):
    """
    The FAO CDK Database Construct is used to create RDS databases.

    The construct automatically enables the following main features:

    -	Compatible with every RDS engine and version;
    -	Create a pre-populated database from RDS snapshots;
    -	Implement High Availability for production databases;
    -	Enable access to the FAO SMTP servers if the databases need to send email notifications (additional configuration at the database level may be required);
    -	Automatic backups and retention configuration according to FAO standards;
    -	Access from the Production Control bastion host server;
    -	Database admin user created using AWS Secret Manager, with password rotation enabled every 30 days;
    -	Encryption at rest of the database storage;
    -	Default or custom RDS parameter group setup;
    -	Adoption of the official database naming convention defined by the CSI database admin team;
    -	Conditionally configure the database removal policy depending on the environment in which the construct is deployed. The policy will be set as `RETAIN` for the Production environment, otherwise set to `DESTROY`;
    -	Conditionally enablement of the deletion protection setup for Production databases;
    -	Private DNS record creation for non-Production environments;
    -	Native integration with the FAO Instance Scheduler to automatically control the uptime of the database;
    -	Conditionally set the license model of Oracle databases;
    -	Enable access from Oracle OEM for Oracle database;
    -	Conditionally export Audit logs to CloudWatch;
    -	Conditionally grant permission to export data to a specified AWS S3 Bucket;
    -	Conditionally tracking of database metrics in the FAO CloudWatch dashboard;

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:

        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliance. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        database_instance_type (str):

        database_name (str): Default=fao_default_schema The main database schema name (for 'Production' environment this must be 'fao_default_schema')

        database_master_username (str): Default="faoadmin" the database admin account username (for 'Production' environment this must be 'faoadmin')

        database_snapshot_id (str): The ARN of the Database Snapshot to restore. The snapshot contains the data that will be inserted into the database. Note that if specified, "DatabaseName" parameter will be ignored.

        database_engine (str): The engine of database you want to create

        database_engine_version (str | aws.aws_rds.DatabaseClusterEngine | aws_neptune_alpha.EngineVersion | aws_cdk_constructs.Database.DocumentDBEngines ): The engine version of database you want to create. Leave blank to get the latest version of the selected database engine (MySQL 5.7, PostgreSQL 10). More info https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engineversion

        database_cluster_parameters_group_name (str):  The name of the DB cluster parameter group to associate with this DB cluster. This parameter depends on the Database Engine version you previously selected. In case you leave blank the version use default.aurora-mysql5.7 or default.aurora-postgresql10. If this argument is omitted, default.aurora5.6 is used. If default.aurora5.6 is used, specifying aurora-mysql or aurora-postgresql for the Engine property might result in an error. More info https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-engineversion

        database_identifier_postfix (str):  An optional RDS database identifier postfix. If not provided the Database instance name will follow the pattern: `app_name` + "-" + `environment` + "-"+ `database_engine`. If provided it will be `app_name` + "-" + `postfix` + "-" + `environment` + "-"+ `database_engine`.

        parameter_group (aws_rds.ParameterGroup | aws_neptune_alpha.ClusterParameter Group): The parameter group to assign to the database cluster

        option_group (aws_rds.OptionGroup): The option group to assign to the database

        database_allocated_storage (str): The size of the allocated space for the database. This is GB

        database_will_send_email (str): If the database should send email

        tag_scheduler_uptime (str): specifies the time range in which the AWS resource should be kept up and running - format `HH:mm-HH:mm` (i.e. 'start'-'end'), where the 'start' time must be before 'end'

        tag_scheduler_uptime_days (str): weekdays in which the `SchedulerUptime` tag should be enforced. If not specified, `SchedulerUptime` will be enforced during each day of the week - format integer from 1 to 7, where 1 is Monday

        tag_scheduler_uptime_skip (str): to skip optimization check - format Boolean (`true`, `false`)

        character_set_name (str):  For supported engines, specifies the character set to associate with the DB instance (Not applicable to Aurora Cluster)

        oracle_license_is_byol (str):  Applicable only to Oracle instances. The default license model is LICENSE_INCLUDED, specify this param in case you want to have an Oracle BRING_YOUR_OWN_LICENSE licence model

        s3_export_buckets (Optional[Sequence[IBucket]]): S3 buckets that you want to load data into. This feature is only supported by the Aurora database engine. This property must not be used if s3ExportRole is used. For MySQL: Default: - None

        s3_import_buckets (Optional[Sequence[IBucket]]): S3 buckets that you want to load data from. This feature is only supported by the Aurora database engine. This property must not be used if s3ImportRole is used. For MySQL: Default: - None

        rubrik_backup (str): to enable/disable Rubrik backup using tag `RubrikBackup` - format Boolean (`true`, `false`). Default: true

        cloudwatch_audit_log (str): Applicable only to relational and Neptune instances. The default is no log exports. Specify this param in case you want to have the audit log export enabled. Neptune: if you also pass a custom cluster parameter group remember to add "neptune_enable_audit_log": "1" to it. If no cluster parameter group is provided it will be added automatically.

        dns_record: (Optional | str) The DNS record associated to the Database if multiple Databases

        create_dns: (Optional | str) to enable/disable dns creation - format Boolean (`true`, `false`). Default: true

        omit_cloudformation_template_outputs(bool): Omit the generation of CloudFormation template outputs. Default: false

        number of instances: (Optional | int): Number of instances for DocumentDB Clusters. Default: 1

    """

    @property
    def security_group(self) -> _ec2.SecurityGroup:
        """Return the database security group

        Returns:
            aws_ec2.SecurityGroup: the database security group
        """
        return self._database_security_group

    @property
    def cluster(self) -> _rds.DatabaseCluster:
        """Return the database cluster

        Returns:
            aws_rds.DatabaseCluster: the database cluster
        """
        return self._cluster

    @property
    def instance(self) -> _rds.DatabaseInstance:
        """Return the database instance

        Returns:
            aws_rds.DatabaseInstance: the database instance
        """
        return self._instance

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name: str,
        environment: str,
        environments_parameters: dict,
        database_type: DatabaseType = DatabaseType.RELATIONAL,
        database_instance_type: str = None,
        database_name: str = None,
        database_master_username: str = 'faoadmin',
        database_snapshot_id: str = None,
        database_engine: str = None,
        database_engine_version: Union[
            str,
            _rds.DatabaseClusterEngine,
            _neptune.EngineVersion,
        ] = None,
        database_cluster_parameters_group_name: str = None,
        database_identifier_postfix: str = '',
        parameter_group: _rds.ParameterGroup = None,
        option_group: _rds.OptionGroup = None,
        database_allocated_storage: str = None,
        database_will_send_email: bool = False,
        tag_scheduler_uptime: str = '',
        tag_scheduler_uptime_days: str = '',
        tag_scheduler_uptime_skip: str = '',
        character_set_name: str = None,
        oracle_license_is_byol: str = None,
        s3_export_buckets: List[aws_cdk.aws_s3.Bucket] = None,
        s3_import_buckets: List[aws_cdk.aws_s3.Bucket] = None,
        rubrik_backup: str = 'True',
        cloudwatch_audit_log: str = None,
        dns_record: str = None,
        create_dns: str = 'True',
        omit_cloudformation_template_outputs: bool = False,
        number_of_instances: int = 1,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)
        self.scope = scope
        self.app_name = app_name
        self._id = id
        self.dashboard = None
        environment = normalize_environment_parameter(environment)
        app_name = app_name.lower().strip()

        # Apply mandatory tags
        cdk.Tags.of(self).add('ApplicationName', app_name)
        cdk.Tags.of(self).add('Environment', environment)

        # Apply FAO CDK tags
        cdk.Tags.of(self).add('fao-cdk-construct', 'database')
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk-version', get_version())
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk', 'true')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create conditions

        environment = environment.lower()
        aws_account = environments_parameters['accounts'][environment]
        vpc = _ec2.Vpc.from_vpc_attributes(
            self,
            'VPC',
            vpc_id=aws_account['vpc'],
            public_subnet_ids=aws_account['public_subnet_ids'],
            private_subnet_ids=aws_account['private_subnet_ids'],
            availability_zones=aws_account['availability_zones'],
        )

        is_production = environment == 'production'
        is_ha = is_production

        sends_emails = (
            database_will_send_email
            and isinstance(database_will_send_email, str)
            and database_will_send_email.lower() == 'true'
        )

        self._instance = None
        self._cluster = None
        self._database_security_group = None

        identifier_postfix = (
            f'-{database_identifier_postfix}'
            if database_identifier_postfix
            else ''
        )
        output_id = f'{app_name}{identifier_postfix}-{environment}-'
        database_identifier = output_id.replace('_', '-')

        to_be_backed_up = (
            rubrik_backup
            and isinstance(rubrik_backup, str)
            and rubrik_backup.lower() == 'true'
        )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CloudFormation outputs
        if not omit_cloudformation_template_outputs:
            cdk.CfnOutput(
                self,
                f'DatabaseAppName{app_name}{output_id}',
                value=str(app_name),
            )
            cdk.CfnOutput(
                self, f'DatabaseIsHa{app_name}{output_id}', value=str(is_ha)
            )
            cdk.CfnOutput(
                self,
                f'DatabaseEngine{app_name}{output_id}',
                value=str(database_engine),
            )
            cdk.CfnOutput(
                self,
                f'DatabaseEngineVersion{app_name}{output_id}',
                value=str(database_engine_version),
            )
            # cdk.CfnOutput(self, f"DatabaseAllocatedStorage{app_name}{output_id}", value=str(database_allocated_storage))
            cdk.CfnOutput(
                self,
                f'DatabaseWillSendEmail{app_name}{output_id}',
                value=str(sends_emails),
            )
            cdk.CfnOutput(
                self,
                f'DatabaseHasBackup{app_name}{output_id}',
                value=str(to_be_backed_up),
            )
            cdk.CfnOutput(
                self,
                f'DatabaseName{app_name}{output_id}',
                value=str(database_name),
            )
            cdk.CfnOutput(
                self,
                f'DatabaseIdentifierPrefix{app_name}{output_id}',
                value=str(database_identifier),
            )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Validate input params

        # TODO

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Retrieve info from already existing AWS resources
        # Important: you need an internet connection!

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create AWS resources

        # ~~~~~~~~~~~~~~~~
        # Security group
        # ~~~~~~~~~~~~~~~~
        self._database_security_group = _ec2.SecurityGroup(
            self,
            'rds_sg',
            vpc=vpc,
            security_group_name=app_name + self._id + 'rds_sg',
            allow_all_outbound=True,
        )

        bastion_host_production_control_security_group = (
            _ec2.SecurityGroup.from_security_group_id(
                self,
                'bastion_host_production_control_security_group',
                aws_account['bastion_host_production_control_security_group'],
                mutable=False,
            )
        )

        security_groups = [
            self._database_security_group,
            bastion_host_production_control_security_group,
        ]

        # Security group to send email
        if sends_emails:
            smtp_access_security_group = (
                _ec2.SecurityGroup.from_security_group_id(
                    self,
                    'smtp_relay_security_group',
                    aws_account['smtp_relay_security_group'],
                    mutable=False,
                )
            )
            security_groups.append(smtp_access_security_group)

        # ~~~~~~~~~~~~~~~~
        # Database
        # ~~~~~~~~~~~~~~~~
        if database_type == DatabaseType.RELATIONAL:
            relational_cluster, relational_instance = RelationalDatabase(
                scope=self,
                app_name=app_name,
                environment=environment,
                environments_parameters=environments_parameters,
                vpc=vpc,
                security_groups=security_groups,
                database_instance_type=database_instance_type,
                database_master_username=database_master_username,
                database_snapshot_id=database_snapshot_id,
                database_engine=database_engine,
                database_identifier=database_identifier,
                is_production=is_production,
                is_ha=is_ha,
                parameter_group=parameter_group,
                database_engine_version=database_engine_version,
                database_cluster_parameters_group_name=database_cluster_parameters_group_name,
                option_group=option_group,
                s3_export_buckets=s3_export_buckets,
                s3_import_buckets=s3_import_buckets,
                database_identifier_postfix=database_identifier_postfix,
                create_dns=create_dns,
                tag_scheduler_uptime=tag_scheduler_uptime,
                tag_scheduler_uptime_days=tag_scheduler_uptime_days,
                tag_scheduler_uptime_skip=tag_scheduler_uptime_skip,
                database_allocated_storage=database_allocated_storage,
                database_name=database_name,
                character_set_name=character_set_name,
                cloudwatch_audit_log=cloudwatch_audit_log,
                dns_record=dns_record,
                oracle_license_is_byol=oracle_license_is_byol,
                to_be_backed_up=to_be_backed_up,
            )

            self._cluster = relational_cluster
            self._instance = relational_instance

        elif database_type == DatabaseType.GRAPH:
            graph_cluster = GraphDatabase(
                scope=self,
                app_name=app_name,
                environment=environment,
                environments_parameters=environments_parameters,
                vpc=vpc,
                security_groups=security_groups,
                database_instance_type=database_instance_type,
                database_identifier=database_identifier,
                is_production=is_production,
                is_ha=is_ha,
                parameter_group=parameter_group,
                database_engine_version=database_engine_version,
                database_cluster_parameters_group_name=database_cluster_parameters_group_name,
                database_identifier_postfix=database_identifier_postfix,
                create_dns=create_dns,
                tag_scheduler_uptime=tag_scheduler_uptime,
                tag_scheduler_uptime_days=tag_scheduler_uptime_days,
                tag_scheduler_uptime_skip=tag_scheduler_uptime_skip,
                cloudwatch_audit_log=cloudwatch_audit_log,
                dns_record=dns_record,
            )

            self._cluster = graph_cluster
        elif database_type == DatabaseType.DOCUMENTAL:
            documentdb_cluster = DocumentDatabase(
                scope=self,
                app_name=app_name,
                environment=environment,
                environments_parameters=environments_parameters,
                vpc=vpc,
                database_instance_type=database_instance_type,
                database_identifier=database_identifier,
                is_production=is_production,
                create_dns=create_dns,
                database_master_username=database_master_username,
                parameter_group=parameter_group,
                database_engine_version=database_engine_version,
                database_identifier_postfix=database_identifier_postfix,
                number_of_instances=number_of_instances,
                tag_scheduler_uptime=tag_scheduler_uptime,
                tag_scheduler_uptime_days=tag_scheduler_uptime_days,
                tag_scheduler_uptime_skip=tag_scheduler_uptime_skip,
                cloudwatch_audit_log=cloudwatch_audit_log,
                dns_record=dns_record,
            )
            self._cluster = documentdb_cluster
        else:
            raise Exception(
                f'Unsupported FAO CDK database_type provided: {database_type}'
            )

    def _get_dashboard(self) -> _cloudwatch.Dashboard:
        path = '_'.join(self.node.path.split('/')[:-1])
        return (
            self.scope.node.try_find_child(f'{self.app_name}-{path}-dashboard')
            or self._create_dashboard()
        )

    def _create_dashboard(self) -> _cloudwatch.Dashboard:
        path = '_'.join(self.node.path.split('/')[:-1])
        return _cloudwatch.Dashboard(
            self.scope,
            f'{self.app_name}-{path}-dashboard',
            dashboard_name=f'{self.app_name}-{path}',
            end='end',
            period_override=_cloudwatch.PeriodOverride.AUTO,
            start='start',
        )

    def render_widgets(self) -> None:
        path = '_'.join(self.node.path.split('/')[:-1])
        self.dashboard = self._get_dashboard()

        if self._cluster:
            self.dashboard.add_widgets(
                _cloudwatch.TextWidget(
                    markdown=f'# {self._id} {path}', width=24
                ),
                _cloudwatch.GraphWidget(
                    left=[self._cluster.metric_cpu_utilization()],
                    title='CPU Utilization',
                ),
                _cloudwatch.GraphWidget(
                    left=[self._cluster.metric_database_connections()],
                    title='DB connections',
                ),
                _cloudwatch.GraphWidget(
                    left=[self._cluster.metric_free_local_storage()],
                    title='Free local storage',
                ),
                _cloudwatch.GraphWidget(
                    left=[
                        self._cluster.metric_network_receive_throughput(),
                        self._cluster.metric_network_transmit_throughput(),
                    ],
                    title='Network throughput',
                ),
            )
        else:
            self.dashboard.add_widgets(
                _cloudwatch.TextWidget(
                    markdown=f'# {self._id} {path}', width=24
                ),
                _cloudwatch.GraphWidget(
                    left=[self._instance.metric_cpu_utilization()],
                    title='CPU Utilization',
                ),
                _cloudwatch.GraphWidget(
                    left=[self._instance.metric_database_connections()],
                    title='DB connections',
                ),
                _cloudwatch.GraphWidget(
                    left=[self._instance.metric_free_storage_space()],
                    title='Free local storage',
                ),
            )
