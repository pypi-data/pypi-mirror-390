from aws_cdk import (
    aws_neptune_alpha as _neptune,
    aws_ec2 as _ec2,
    aws_kms as _kms,
    aws_route53 as route53,
    RemovalPolicy as removal_policy,
    aws_logs as _logs,
)
import aws_cdk as cdk
from typing import Union, List


def GraphDatabase(
    scope,
    app_name: str,
    environment: str,
    environments_parameters: dict,
    vpc: _ec2.Vpc,
    security_groups: List[_ec2.SecurityGroup],
    database_instance_type: str,
    database_identifier: str,
    is_production: bool,
    is_ha: bool,
    parameter_group: _neptune.ParameterGroup = None,
    database_engine_version: Union[str, _neptune.EngineVersion] = None,
    database_cluster_parameters_group_name: str = None,
    database_identifier_postfix: str = '',
    create_dns: str = 'True',
    tag_scheduler_uptime: str = '',
    tag_scheduler_uptime_days: str = '',
    tag_scheduler_uptime_skip: str = '',
    cloudwatch_audit_log: str = None,
    dns_record: str = None,
):
    environment = environment.lower()
    aws_account = environments_parameters['accounts'][environment]
    account_id = aws_account['id']

    is_not_production = not is_production

    _cluster = None

    # ~~~~~~~~~~~~~~~~
    # RDS Instance type
    # ~~~~~~~~~~~~~~~~
    instance_type = _neptune.InstanceType.of(database_instance_type)

    # ~~~~~~~~~~~~~~~~
    # KMS Encryption key
    # ~~~~~~~~~~~~~~~~
    key_arn = (
        'arn:aws:kms:eu-west-1:'
        + account_id
        + ':key/'
        + aws_account['kms_neptune_key']
    )
    encryption_key = _kms.Key.from_key_arn(scope, 'encryption_key', key_arn)

    # ~~~~~~~~~~~~~~~~
    # Neptune Logs
    # ~~~~~~~~~~~~~~~~
    # Default Neptune cloudwatch logs export in NONE
    cloudwatch_logs_exports = None
    should_be_cloudwatch_audit_log = (
        cloudwatch_audit_log
        and isinstance(cloudwatch_audit_log, str)
        and cloudwatch_audit_log.lower() == 'true'
    )

    if should_be_cloudwatch_audit_log:
        # If user specified change to cloud watch log setting
        cloudwatch_logs_exports = [_neptune.LogType.AUDIT]

    # ~~~~~~~~~~~~~~~~
    # Neptune Parameter group
    # ~~~~~~~~~~~~~~~~
    default_cluster_params = {}
    if should_be_cloudwatch_audit_log:
        default_cluster_params.update({'neptune_enable_audit_log': '1'})

    my_parameter_group = parameter_group or _neptune.ClusterParameterGroup(
        scope,
        f'{app_name}cluster_params',
        description=f'{app_name} - Cluster parameter group',
        parameters=default_cluster_params,
        family=_neptune.ParameterGroupFamily.NEPTUNE_1_2,
    )

    my_engine_version = (
        database_engine_version
        if database_engine_version
        else _neptune.EngineVersion.V1_2_1_0
    )

    # ~~~~~~~~~~~~~~~~
    # Neptune Cluster
    # ~~~~~~~~~~~~~~~~
    _cluster = _neptune.DatabaseCluster(
        scope,
        'cluster',
        instance_type=instance_type,
        vpc=vpc,
        # associated_roles=None,
        auto_minor_version_upgrade=False,
        backup_retention=cdk.Duration.days(30),
        cloudwatch_logs_exports=cloudwatch_logs_exports,
        cloudwatch_logs_retention=_logs.RetentionDays.ONE_MONTH,
        # cloudwatch_logs_retention_role=None, # Create a new role
        cluster_parameter_group=my_parameter_group,
        db_cluster_name=database_identifier + 'cluster',
        deletion_protection=is_production,
        engine_version=my_engine_version,
        # iam_authentication=None
        instance_identifier_base=database_identifier,
        instances=2 if is_ha else 1,
        kms_key=encryption_key,
        # parameter_group=None TODO: implement when this will be needed
        preferred_backup_window='01:00-02:00',
        preferred_maintenance_window='mon:03:00-mon:04:00',
        removal_policy=removal_policy.RETAIN
        if is_production
        else removal_policy.DESTROY,
        security_groups=security_groups,
        storage_encrypted=True,
        # subnet_group=None, # Use default value, create a new subnet group
        # vpc_subnets=None, # Do not specify to host the db in the private subnets
    )

    if not is_production and create_dns.lower() == 'true':
        # Create DNS record
        cluster_hostname = str(_cluster.cluster_endpoint)
        cluster_hostname = ''.join(cluster_hostname.split())

        hosted_zone_id = aws_account['route53_hosted_zone_id']
        domain_name = aws_account['route53_domain_name']

        dns_record = 'db.' + app_name if app_name else dns_record
        dns_record = (
            dns_record + '-' + database_identifier_postfix
            if database_identifier_postfix
            else dns_record
        )
        route53_zone = route53.PrivateHostedZone.from_hosted_zone_attributes(
            scope,
            f'RDSPrivateHostedZone{dns_record}',
            hosted_zone_id=hosted_zone_id,
            zone_name=domain_name,
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

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Scheduler tags
    if is_not_production:
        clus = _cluster.node.find_child('Resource')
        instance = _cluster.node.find_child('Instance1')

        if tag_scheduler_uptime_skip:
            cdk.Tags.of(clus).add('SchedulerSkip', tag_scheduler_uptime_skip)
            cdk.Tags.of(instance).add(
                'SchedulerSkip', tag_scheduler_uptime_skip
            )

        if tag_scheduler_uptime:
            cdk.Tags.of(clus).add('SchedulerUptime', tag_scheduler_uptime)
            cdk.Tags.of(instance).add('SchedulerUptime', tag_scheduler_uptime)

        if tag_scheduler_uptime_days:
            cdk.Tags.of(clus).add(
                'SchedulerUptimeDays', tag_scheduler_uptime_days
            )
            cdk.Tags.of(instance).add(
                'SchedulerUptimeDays', tag_scheduler_uptime_days
            )

    # ~~~~~~~~~~~~~~~~
    # Return
    # ~~~~~~~~~~~~~~~~
    return _cluster
