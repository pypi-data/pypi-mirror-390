from enum import Enum
from typing import List

import aws_cdk as cdk
from aws_cdk import (
    aws_docdb as _docdb,
    aws_ec2 as _ec2,
    aws_kms as _kms,
    aws_route53 as _route53,
    aws_logs as _logs,
)


class DocumentDBEngines(Enum):
    v4_0_0 = '4.0.0'
    v3_0_0 = '3.0.0'
    v5_0_0 = '5.0.0'


engine_to_parameter_group_name = {
    '3.0.0': 'default.docdb3.0',
    '4.0.0': 'default.docdb4.0',
    '5.0.0': 'default.docdb5.0',
}


def DocumentDatabase(
    scope,
    app_name: str,
    environment: str,
    environments_parameters: dict,
    vpc: _ec2.Vpc,
    database_instance_type: str,
    database_identifier: str,
    is_production: bool,
    create_dns: str = 'True',
    database_master_username: str = 'faoadmin',
    parameter_group: _docdb.ClusterParameterGroup = None,
    database_engine_version: DocumentDBEngines = DocumentDBEngines.v5_0_0,
    database_identifier_postfix: str = '',
    number_of_instances: int = 1,
    tag_scheduler_uptime: str = '',
    tag_scheduler_uptime_days: str = '',
    tag_scheduler_uptime_skip: str = '',
    cloudwatch_audit_log: bool = False,
    security_groups: List[_ec2.SecurityGroup] = None,
    dns_record: str = None,
) -> _docdb.DatabaseCluster:
    environment = environment.lower()
    aws_account = environments_parameters['accounts'][environment]
    account_id = aws_account['id']

    instance_type = _ec2.InstanceType(database_instance_type)

    if not database_engine_version:
        database_engine_version = DocumentDBEngines.v5_0_0

    if not parameter_group:
        parameter_group_name = engine_to_parameter_group_name.get(
            database_engine_version.value
        )
        parameter_group = (
            _docdb.ClusterParameterGroup.from_parameter_group_name(
                scope=scope,
                id='docdb-parameterGroup',
                parameter_group_name=parameter_group_name,
            )
        )

    # ~~~~~~~~~~~~~~~~
    # KMS Encryption key
    # ~~~~~~~~~~~~~~~~
    key_arn = (
        'arn:aws:kms:eu-west-1:'
        + account_id
        + ':key/'
        + aws_account['kms_documentdb_key']
    )
    encryption_key = _kms.Key.from_key_arn(scope, 'encryption_key', key_arn)
    _cluster = _docdb.DatabaseCluster(
        scope=scope,
        id=app_name + '_docdb',
        instance_type=instance_type,
        master_user=_docdb.Login(username=database_master_username),
        vpc=vpc,
        backup=_docdb.BackupProps(
            retention=cdk.Duration.days(30), preferred_window='01:00-02:00'
        ),
        cloud_watch_logs_retention=_logs.RetentionDays.ONE_MONTH,
        db_cluster_name=database_identifier + 'cluster',
        deletion_protection=is_production,
        engine_version=database_engine_version.value,
        export_audit_logs_to_cloud_watch=cloudwatch_audit_log,
        instances=number_of_instances,
        kms_key=encryption_key,
        parameter_group=parameter_group,
        preferred_maintenance_window='mon:03:00-mon:04:00',
        removal_policy=cdk.RemovalPolicy.RETAIN
        if is_production
        else cdk.RemovalPolicy.DESTROY,
        storage_encrypted=True,
    )
    if security_groups:
        for sg in security_groups:
            _cluster.add_security_groups(sg)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DNS record
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
        route53_zone = _route53.PrivateHostedZone.from_hosted_zone_attributes(
            scope,
            f'RDSPrivateHostedZone{dns_record}',
            hosted_zone_id=hosted_zone_id,
            zone_name=domain_name,
        )
        _route53.CnameRecord(
            scope,
            f'RDSAliasRecord{dns_record}',
            zone=route53_zone,
            # target=cdk.Token.as_string(self._cluster.cluster_endpoint), # << Not working here
            # target=route53.RecordTarget.from_values(self._cluster.cluster_endpoint.hostname),
            domain_name=cluster_hostname,
            record_name=f'{dns_record}.{domain_name}',
        )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FAO AWS Scheduler tags
    if not is_production:
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

    return _cluster
