from aws_cdk import (
    aws_rds as _rds,
    aws_ec2 as _ec2,
    aws_kms as _kms,
    aws_route53 as route53,
    aws_iam as _iam,
    aws_logs as _logs,
    custom_resources as _cr,
)
import aws_cdk as cdk
from typing import Union, List


engine_to_cdk_engine = {
    'legacy-aurora-mysql': _rds.DatabaseClusterEngine.aurora,
    'aurora-mysql': _rds.DatabaseClusterEngine.aurora_mysql,
    'aurora-postgresql': _rds.DatabaseClusterEngine.aurora_postgres,
    'aurora-postgresql-12': _rds.DatabaseClusterEngine.aurora_postgres,
    'oracle_s2': _rds.DatabaseInstanceEngine.oracle_se2,
    'oracle_ee': _rds.DatabaseInstanceEngine.oracle_ee,
    'mysql': _rds.DatabaseInstanceEngine.mysql,
    'postgresql': _rds.DatabaseInstanceEngine.postgres,
    'sqlserver-se': _rds.DatabaseInstanceEngine.sql_server_se,
    'sqlserver-ex': _rds.DatabaseInstanceEngine.sql_server_ex,
}

engine_to_cluster_parameter_group_family = {
    'legacy-aurora-mysql': 'default.aurora5.6',
    'aurora-mysql': 'default.aurora-mysql5.7',
    'aurora-postgresql': 'default.aurora-postgresql9.6',
    'aurora-postgresql-12': 'default.aurora-postgresql12',
    'oracle_s2': 'default.oracle-se2-19',
    'oracle_ee': 'default.oracle-ee-19',
    'mysql': 'default.mysql5.7',
    'postgresql': None,
    'sqlserver-se': 'default.sqlserver-se-14.0',
    'sqlserver-ex': 'default.sqlserver-ex-14.0',
}

engine_to_version_class = {
    'legacy-aurora-mysql': _rds.AuroraEngineVersion,
    'aurora-mysql': _rds.AuroraMysqlEngineVersion,
    'mysql': _rds.MysqlEngineVersion,
    'oracle_s2': _rds.OracleEngineVersion,
    'oracle_ee': _rds.OracleEngineVersion,
    'aurora-postgresql': _rds.AuroraPostgresEngineVersion,
    'aurora-postgresql-12': _rds.AuroraPostgresEngineVersion,
    'postgresql': _rds.PostgresEngineVersion,
    'sqlserver-se': _rds.SqlServerEngineVersion,
    'sqlserver-ex': _rds.SqlServerEngineVersion,
}


def get_engine(
    database_engine: str, database_engine_version: str
) -> Union[_rds.DatabaseClusterEngine, _rds.DatabaseInstanceEngine]:
    """Return the database engine as string

    Returns:
        str: the database engine as string
    """
    # For MySQL engine: extract db major version
    major_version = database_engine_version.split('.')
    major_version = major_version[:-1]
    major_version = '.'.join(major_version)

    return engine_to_cdk_engine[database_engine](
        # version=database_engine_version if database_engine_version else None
        version=engine_to_version_class[database_engine].of(
            database_engine_version, major_version
        )
    )


def RelationalDatabase(
    scope,
    app_name: str,
    environment: str,
    environments_parameters: dict,
    vpc: _ec2.Vpc,
    security_groups: List[_ec2.SecurityGroup],
    database_instance_type: str,
    database_master_username: str,
    database_snapshot_id: str,
    database_engine: str,
    database_identifier: str,
    is_production: bool,
    is_ha: bool,
    parameter_group: _rds.ParameterGroup = None,
    database_engine_version: Union[str, _rds.DatabaseClusterEngine] = None,
    database_cluster_parameters_group_name: str = None,
    option_group: _rds.OptionGroup = None,
    s3_export_buckets: str = None,
    s3_import_buckets: str = None,
    database_identifier_postfix: str = '',
    create_dns: str = 'True',
    to_be_backed_up: bool = True,
    tag_scheduler_uptime: str = '',
    tag_scheduler_uptime_days: str = '',
    tag_scheduler_uptime_skip: str = '',
    database_allocated_storage: str = None,
    database_name: str = None,
    character_set_name: str = None,
    cloudwatch_audit_log: str = None,
    dns_record: str = None,
    oracle_license_is_byol: str = None,
):

    environment = environment.lower()
    aws_account = environments_parameters['accounts'][environment]
    account_id = aws_account['id']

    use_snapshot = database_snapshot_id

    is_not_production = not is_production

    is_cluster_compatible = 'aurora' in database_engine
    is_not_cluster_compatible = not is_cluster_compatible

    is_oracle = 'oracle' in database_engine
    is_sqlserver = 'sqlserver' in database_engine
    is_sqlserver_ex = 'sqlserver-ex' in database_engine

    has_no_parameter_group = (
        parameter_group is None
        and database_cluster_parameters_group_name is None
    )
    has_no_default_parameter_group = (
        has_no_parameter_group
        and engine_to_cluster_parameter_group_family[database_engine] is None
    )

    has_no_option_group = option_group is None

    _instance = None
    _cluster = None

    # ~~~~~~~~~~~~~~~~
    # RDS Instance type
    # ~~~~~~~~~~~~~~~~
    instance_type = _ec2.InstanceType(database_instance_type)
    instance_props = _rds.InstanceProps(
        instance_type=instance_type,
        vpc=vpc,
        security_groups=security_groups,
    )

    # ~~~~~~~~~~~~~~~~
    # AWS Secret Manager
    # ~~~~~~~~~~~~~~~~
    credentials = _rds.Credentials.from_username(database_master_username)

    # ~~~~~~~~~~~~~~~~
    # KMS Encryption key
    # ~~~~~~~~~~~~~~~~
    # SQL Server Express does not support encryption
    if not is_sqlserver_ex:
        key_arn = (
            'arn:aws:kms:eu-west-1:'
            + account_id
            + ':key/'
            + aws_account['kms_rds_key']
        )
        encryption_key = _kms.Key.from_key_arn(
            scope, 'encryption_key', key_arn
        )
    else:
        encryption_key = None

    # ~~~~~~~~~~~~~~~~
    # RDS Parameter group
    # ~~~~~~~~~~~~~~~~
    my_parameter_group = None
    if has_no_default_parameter_group is False:
        my_parameter_group = (
            parameter_group
            or _rds.ParameterGroup.from_parameter_group_name(
                scope,
                'parameter_group',
                parameter_group_name=database_cluster_parameters_group_name
                if database_cluster_parameters_group_name
                else engine_to_cluster_parameter_group_family[database_engine],
            )
        )

    # ~~~~~~~~~~~~~~~~
    # RDS Database engine
    # ~~~~~~~~~~~~~~~~
    _engine = (
        (get_engine(database_engine, database_engine_version))
        if isinstance(database_engine_version, str)
        else database_engine_version
    )

    should_be_cloudwatch_audit_log = (
        cloudwatch_audit_log
        and isinstance(cloudwatch_audit_log, str)
        and cloudwatch_audit_log.lower() == 'true'
    )

    cloudwatch_logs_exports = None
    cloudwatch_logs_retention = None
    if should_be_cloudwatch_audit_log and is_production:
        logs_service_user = _iam.User(
            scope,
            id='logs_service_user',
            managed_policies=None,
            user_name=f'SRVUSR-{app_name}_{environment}_logs',
        )
        logs_service_user_policies = _iam.ManagedPolicy(
            scope,
            'logs_service_user_policies',
            statements=[
                # S3 Configuration bucket permissions
                _iam.PolicyStatement(
                    actions=[
                        'logs:GetLogEvents',
                    ],
                    resources=[
                        f'arn:aws:logs:eu-west-1:{account_id}:log-group:/aws/rds/*/{app_name}*:log-stream:*',
                    ],
                ),
                _iam.PolicyStatement(
                    actions=[
                        'logs:DescribeLogGroups',
                        'logs:DescribeLogStreams',
                    ],
                    resources=[
                        f'arn:aws:logs:eu-west-1:{account_id}:log-group:/aws/rds/*/{app_name}*',
                    ],
                ),
            ],
        )
        logs_service_user.add_managed_policy(logs_service_user_policies)
        # If user specified change to cloud watch log setting
        cloudwatch_logs_exports = _rds.cloudwatch_logs_exports = ['audit']
        cloudwatch_logs_retention = _logs.RetentionDays.TWO_WEEKS

    # ~~~~~~~~~~~~~~~~
    # RDS Cluster
    # ~~~~~~~~~~~~~~~~
    if is_cluster_compatible:
        _cluster = _rds.DatabaseCluster(
            scope,
            'cluster',
            engine=_engine,
            instance_props=instance_props,
            credentials=credentials,
            cluster_identifier=database_identifier + database_engine,
            instance_identifier_base=database_identifier,
            deletion_protection=is_production,
            # No need to create instance resource, only specify the amount
            instances=2 if is_ha else 1,
            backup=_rds.BackupProps(
                retention=cdk.Duration.days(30),
                preferred_window='01:00-02:00',
            ),
            default_database_name='fao_default_schema',
            preferred_maintenance_window='mon:03:00-mon:04:00',
            parameter_group=my_parameter_group,
            storage_encryption_key=encryption_key,
            s3_export_buckets=s3_export_buckets,
            s3_import_buckets=s3_import_buckets,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
        )

        _cluster.add_rotation_single_user(
            automatically_after=cdk.Duration.days(30)
        )
        if not is_production and create_dns.lower() == 'true':
            # Create DNS record
            cluster_hostname = str(_cluster.cluster_endpoint.hostname)
            cluster_hostname = ''.join(cluster_hostname.split())

            hosted_zone_id = aws_account['route53_hosted_zone_id']
            domain_name = aws_account['route53_domain_name']

            dns_record = 'db.' + app_name if app_name else dns_record
            dns_record = (
                dns_record + '-' + database_identifier_postfix
                if database_identifier_postfix
                else dns_record
            )
            route53_zone = (
                route53.PrivateHostedZone.from_hosted_zone_attributes(
                    scope,
                    f'RDSPrivateHostedZone{dns_record}',
                    hosted_zone_id=hosted_zone_id,
                    zone_name=domain_name,
                )
            )
            route53.CnameRecord(
                scope,
                f'RDSAliasRecord{dns_record}',
                zone=route53_zone,
                # target=cdk.Token.as_string(self._cluster.cluster_endpoint), # << Not working here
                # target=route53.RecordTarget.from_values(self._cluster.cluster_endpoint.hostname),
                domain_name=cluster_hostname,
                record_name=f'{dns_record}.{domain_name}',
            )

        # Conditionally create a cluster from a snapshot
        if use_snapshot:
            _cluster.node.find_child('Resource').add_property_override(
                'SnapshotIdentifier', database_snapshot_id
            )
            # While creating an RDS from a snapshot, MasterUsername cannot be specified
            _cluster.node.find_child('Resource').add_property_override(
                'MasterUsername', None
            )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Scheduler tags
        if is_not_production:
            clus = _cluster.node.find_child('Resource')
            instance = _cluster.node.find_child('Instance1')

            if tag_scheduler_uptime_skip:
                cdk.Tags.of(clus).add(
                    'SchedulerSkip', tag_scheduler_uptime_skip
                )
                cdk.Tags.of(instance).add(
                    'SchedulerSkip', tag_scheduler_uptime_skip
                )

            if tag_scheduler_uptime:
                cdk.Tags.of(clus).add('SchedulerUptime', tag_scheduler_uptime)
                cdk.Tags.of(instance).add(
                    'SchedulerUptime', tag_scheduler_uptime
                )

            if tag_scheduler_uptime_days:
                cdk.Tags.of(clus).add(
                    'SchedulerUptimeDays', tag_scheduler_uptime_days
                )
                cdk.Tags.of(instance).add(
                    'SchedulerUptimeDays', tag_scheduler_uptime_days
                )

        if should_be_cloudwatch_audit_log and is_production:
            # Tag LogGroup
            log_group_name = (
                f'/aws/rds/cluster/{_cluster.cluster_identifier}/audit'
            )
            log_group_tags = {
                'ApplicationName': app_name,
                'Environment': environment,
                'DatabaseAuditLog': app_name,
            }
            _cr.AwsCustomResource(
                scope,
                f'TagClusterLogGroupAudit',
                on_create=_cr.AwsSdkCall(
                    service='CloudWatchLogs',
                    action='TagLogGroup',
                    parameters={
                        'logGroupName': log_group_name,
                        'tags': log_group_tags,
                    },
                    physical_resource_id=_cr.PhysicalResourceId.of(
                        log_group_name
                    ),
                ),
                on_update=_cr.AwsSdkCall(
                    service='CloudWatchLogs',
                    action='TagLogGroup',
                    parameters={
                        'logGroupName': log_group_name,
                        'tags': log_group_tags,
                    },
                    physical_resource_id=_cr.PhysicalResourceId.of(
                        log_group_name
                    ),
                ),
                on_delete=_cr.AwsSdkCall(
                    service='CloudWatchLogs',
                    action='TagLogGroup',
                    parameters={
                        'logGroupName': log_group_name,
                        'tags': log_group_tags,
                    },
                    physical_resource_id=_cr.PhysicalResourceId.of(
                        log_group_name
                    ),
                ),
                policy=_cr.AwsCustomResourcePolicy.from_sdk_calls(
                    resources=_cr.AwsCustomResourcePolicy.ANY_RESOURCE
                ),
            )

    # ~~~~~~~~~~~~~~~~
    # RDS Instance
    # ~~~~~~~~~~~~~~~~
    if is_not_cluster_compatible:

        # Default RDS license model is NONE
        license_model = None
        # Default RDS cloudwatch logs export in NONE
        # cloudwatch_logs_exports = None

        if is_oracle:

            # Default Oracle license model is LICENSE_INCLUDED
            license_model = _rds.LicenseModel.LICENSE_INCLUDED

            oracle_oem_client_security_group = (
                _ec2.SecurityGroup.from_security_group_id(
                    scope,
                    'oracle_oem_client_security_group',
                    aws_account['oracle_oem_client_security_group'],
                    mutable=False,
                )
            )
            security_groups.append(oracle_oem_client_security_group)

            should_be_byol_oracle_license_model = (
                oracle_license_is_byol
                and isinstance(oracle_license_is_byol, str)
                and oracle_license_is_byol.lower() == 'true'
            )

            if should_be_byol_oracle_license_model:
                # If user specified change to BRING_YOUR_OWN_LICENSE
                license_model = _rds.LicenseModel.BRING_YOUR_OWN_LICENSE

        if is_sqlserver:
            # Default SQL server license model is LICENSE_INCLUDED
            license_model = _rds.LicenseModel.LICENSE_INCLUDED

        if is_sqlserver_ex or not is_production:
            is_multi_az = False
        else:
            is_multi_az = True

        _instance = _rds.DatabaseInstance(
            scope,
            'instance',
            engine=_engine,
            allocated_storage=database_allocated_storage
            and int(database_allocated_storage),
            allow_major_version_upgrade=False,
            database_name=database_name if database_name else None,
            license_model=license_model,
            credentials=credentials,
            parameter_group=my_parameter_group,
            instance_type=instance_type,
            vpc=vpc,
            auto_minor_version_upgrade=True,
            backup_retention=cdk.Duration.days(30),
            copy_tags_to_snapshot=True,
            deletion_protection=is_production,
            instance_identifier=database_identifier + 'db',
            # max_allocated_storage=None,
            multi_az=is_multi_az,
            option_group=None if has_no_option_group else option_group,
            preferred_maintenance_window='mon:03:00-mon:04:00',
            processor_features=None,
            security_groups=security_groups,
            storage_encryption_key=encryption_key,
            character_set_name=character_set_name,
            cloudwatch_logs_exports=cloudwatch_logs_exports,
            cloudwatch_logs_retention=cloudwatch_logs_retention,
            s3_export_buckets=s3_export_buckets,
            s3_import_buckets=s3_import_buckets,
        )

        if s3_export_buckets or s3_import_buckets:
            # This fix is required to enable SQL server integration with S3.
            # Default CDK generated permissions are not enough
            s3_import_policy = (
                _instance.node.find_child('S3ImportRole')
                .node.find_child('DefaultPolicy')
                .node.default_child
            )
            rds_s3_list_statement = _iam.PolicyStatement(
                actions=['s3:ListAllMyBuckets'],
                resources=['*'],
            )
            s3_import_policy.policy_document.add_statements(
                rds_s3_list_statement
            )

        # Conditionally create an instance from a snapshot
        if use_snapshot:
            _instance.node.find_child('Resource').add_property_override(
                'DBSnapshotIdentifier', database_snapshot_id
            )
            # While creating an RDS from a snapshot, MasterUsername cannot be specified
            _instance.node.find_child('Resource').add_property_override(
                'MasterUsername', None
            )

        _instance.add_rotation_single_user(
            automatically_after=cdk.Duration.days(30)
        )

        # Create DNS record
        if not is_production:
            instance_hostname = str(_instance.instance_endpoint.hostname)
            instance_hostname = ''.join(instance_hostname.split())

            hosted_zone_id = aws_account['route53_hosted_zone_id']
            domain_name = aws_account['route53_domain_name']

            dns_record = 'db.' + app_name if app_name else dns_record
            dns_record = (
                dns_record + '-' + database_identifier_postfix
                if database_identifier_postfix
                else dns_record
            )
            route53_zone = (
                route53.PrivateHostedZone.from_hosted_zone_attributes(
                    scope,
                    f'RDSPrivateHostedZone{dns_record}',
                    hosted_zone_id=hosted_zone_id,
                    zone_name=domain_name,
                )
            )
            route53.CnameRecord(
                scope,
                f'RDSAliasRecord{dns_record}',
                zone=route53_zone,
                domain_name=instance_hostname,
                record_name=f'{dns_record}.{domain_name}',
            )

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Rubrik backup tag

        if to_be_backed_up:
            cdk.Tags.of(_instance).add('RubrikBackup', 'true')
        else:
            cdk.Tags.of(_instance).add('RubrikBackup', 'false')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Scheduler tags
        if is_not_production:
            instance = _instance.node.find_child('Resource')
            if tag_scheduler_uptime_skip:
                cdk.Tags.of(instance).add(
                    'SchedulerSkip', tag_scheduler_uptime_skip
                )

            if tag_scheduler_uptime:
                cdk.Tags.of(instance).add(
                    'SchedulerUptime', tag_scheduler_uptime
                )

            if tag_scheduler_uptime_days:
                cdk.Tags.of(instance).add(
                    'SchedulerUptimeDays', tag_scheduler_uptime_days
                )

        if should_be_cloudwatch_audit_log and is_production:
            # Tag LogGroup
            log_group_name = (
                f'/aws/rds/instance/{_instance.instance_identifier}/audit'
            )
            log_group_tags = {
                'ApplicationName': app_name,
                'Environment': environment,
                'DatabaseAuditLog': app_name,
            }
            _cr.AwsCustomResource(
                scope,
                f'TagInstanceLogGroupAudit',
                on_create=_cr.AwsSdkCall(
                    service='CloudWatchLogs',
                    action='TagLogGroup',
                    parameters={
                        'logGroupName': log_group_name,
                        'tags': log_group_tags,
                    },
                    physical_resource_id=_cr.PhysicalResourceId.of(
                        log_group_name
                    ),
                ),
                on_update=_cr.AwsSdkCall(
                    service='CloudWatchLogs',
                    action='TagLogGroup',
                    parameters={
                        'logGroupName': log_group_name,
                        'tags': log_group_tags,
                    },
                    physical_resource_id=_cr.PhysicalResourceId.of(
                        log_group_name
                    ),
                ),
                on_delete=_cr.AwsSdkCall(
                    service='CloudWatchLogs',
                    action='TagLogGroup',
                    parameters={
                        'logGroupName': log_group_name,
                        'tags': log_group_tags,
                    },
                    physical_resource_id=_cr.PhysicalResourceId.of(
                        log_group_name
                    ),
                ),
                policy=_cr.AwsCustomResourcePolicy.from_sdk_calls(
                    resources=_cr.AwsCustomResourcePolicy.ANY_RESOURCE
                ),
            )

    # ~~~~~~~~~~~~~~~~
    # Returns
    # ~~~~~~~~~~~~~~~~
    return _cluster, _instance
