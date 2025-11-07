import aws_cdk.aws_s3
from aws_cdk import aws_docdb as _docdb, Duration
import pytest
from aws_cdk.assertions import Template, Match
from aws_cdk_constructs import Database, DatabaseType
from aws_cdk_constructs import Bucket


@pytest.fixture
def database_default_parameters(stack, environment_parameters):
    return {
        'scope': stack,
        'id': 'test-database-id',
        'app_name': 'test-app',
        'environment': 'Development',
        'environments_parameters': environment_parameters,
        'database_instance_type': 'db.t3.micro',
    }


@pytest.fixture
def database_graph_default_parameters(stack, environment_parameters):
    return {
        'scope': stack,
        'id': 'test-neptune-database-id',
        'app_name': 'test-app',
        'environment': 'Development',
        'environments_parameters': environment_parameters,
        'database_type': DatabaseType.GRAPH,
        'database_instance_type': 'db.t4g.medium',
        'database_identifier_postfix': 'neptune',
    }


@pytest.fixture
def database_documentdb_default_parameters(stack, environment_parameters):
    return {
        'scope': stack,
        'id': 'test-documentdb-database-id',
        'app_name': 'test-app',
        'environment': 'Development',
        'environments_parameters': environment_parameters,
        'database_type': DatabaseType.DOCUMENTAL,
        'database_instance_type': 't4g.medium',
        'database_identifier_postfix': 'documentdb',
    }


@pytest.fixture
def aurora_cluster_parameters(
    stack, environment_parameters, database_default_parameters
):
    database_default_parameters['database_engine'] = 'aurora-mysql'
    database_default_parameters['database_engine_version'] = '5.7'
    return database_default_parameters


@pytest.fixture()
def postgres_instance_parameters(
    stack, environment_parameters, database_default_parameters
):
    database_default_parameters['database_engine'] = 'postgresql'
    database_default_parameters['database_engine_version'] = '12.4'
    return database_default_parameters


@pytest.fixture()
def sqlserver_ex_instance_parameters(
    stack, environment_parameters, database_default_parameters
):
    database_default_parameters['database_engine'] = 'sqlserver-ex'
    database_default_parameters['database_engine_version'] = '14.0"'
    return database_default_parameters


@pytest.fixture()
def sqlserver_se_instance_parameters(
    stack, environment_parameters, database_default_parameters
):
    database_default_parameters['database_engine'] = 'sqlserver-se'
    database_default_parameters['database_engine_version'] = '12.4'
    return database_default_parameters


@pytest.fixture()
def oracle_instance_parameters(
    stack, environment_parameters, database_default_parameters
):
    database_default_parameters['database_engine'] = 'oracle_ee'
    database_default_parameters['database_engine_version'] = '19'
    return database_default_parameters


def test_database_has_mandatory_tags(
    app, stack, environment_parameters, postgres_instance_parameters
):
    Database(**postgres_instance_parameters)
    from aws_cdk_constructs.utils import get_version

    version = get_version()
    mandatory_tags = {
        'Tags': Match.array_with(
            [
                {'Key': 'ApplicationName', 'Value': 'test-app'},
                {'Key': 'Environment', 'Value': 'Development'},
                {'Key': 'fao-cdk', 'Value': 'true'},
                {'Key': 'fao-cdk-construct', 'Value': 'database'},
                {'Key': 'fao-cdk-version', 'Value': version},
            ]
        )
    }
    template = Template.from_stack(stack)
    template.has_resource_properties('AWS::RDS::DBInstance', mandatory_tags)
    template.has_resource_properties('AWS::RDS::DBSubnetGroup', mandatory_tags)
    template.has_resource_properties(
        'AWS::SecretsManager::Secret', mandatory_tags
    )
    template.has_resource_properties('AWS::EC2::SecurityGroup', mandatory_tags)
    # Serverless application does not follow the same pattern of key/value ¯\_(ツ)_/¯
    template.has_resource_properties(
        'AWS::Serverless::Application',
        {
            'Tags': {
                'ApplicationName': 'test-app',
                'Environment': 'Development',
                'fao-cdk': 'true',
                'fao-cdk-construct': 'database',
                'fao-cdk-version': version,
            }
        },
    )


def test_database_has_its_own_sg(
    app, stack, environment_parameters, postgres_instance_parameters
):
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupName': 'test-apptest-database-idrds_sg',
                'SecurityGroupEgress': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Allow '
                        'all '
                        'outbound '
                        'traffic '
                        'by '
                        'default',
                        'IpProtocol': '-1',
                    }
                ],
            }
        },
    )
    sg_id = list(sg.keys())[0]
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {
            'VPCSecurityGroups': Match.array_with(
                [{'Fn::GetAtt': [sg_id, 'GroupId']}]
            )
        },
    )


def test_database_has_prodctl_sg(
    app, stack, environment_parameters, postgres_instance_parameters
):
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'VPCSecurityGroups': Match.array_with(['sg-prodctl'])},
    )


def test_database_send_emails_have_sg(
    app, stack, environment_parameters, postgres_instance_parameters
):
    postgres_instance_parameters['database_will_send_email'] = 'true'
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'VPCSecurityGroups': Match.array_with(['smtp-relay-sg-id'])},
    )


def test_database_has_encryption(
    app, stack, environment_parameters, postgres_instance_parameters
):
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance', {'StorageEncrypted': True}
    )


def test_database_has_not_encryption_if_sqlserver_ex(
    app, stack, environment_parameters, sqlserver_ex_instance_parameters
):
    Database(**sqlserver_ex_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance', Match.not_({'StorageEncrypted': False})
    )


def test_database_creates_default_user(
    app, stack, environment_parameters, postgres_instance_parameters
):
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::SecretsManager::Secret',
        {
            'GenerateSecretString': {
                'PasswordLength': 30,
                'SecretStringTemplate': '{"username":"faoadmin"}',
                'ExcludeCharacters': ' ' '%+~`#$&*()|[]{}:;<>?!\'/@"\\',
                'GenerateStringKey': 'password',
            }
        },
    )


def test_database_creates_custom_user(
    app, stack, environment_parameters, postgres_instance_parameters
):
    postgres_instance_parameters['database_master_username'] = 'test-user'
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::SecretsManager::Secret',
        {
            'GenerateSecretString': {
                'PasswordLength': 30,
                'SecretStringTemplate': '{"username":"test-user"}',
                'ExcludeCharacters': ' ' '%+~`#$&*()|[]{}:;<>?!\'/@"\\',
                'GenerateStringKey': 'password',
            }
        },
    )


def test_database_with_no_parameter_group(
    app, stack, environment_parameters, postgres_instance_parameters
):
    Database(**postgres_instance_parameters)

    template = Template.from_stack(stack)
    template.resource_count_is('AWS::RDS::DBParameterGroup', 0)


def test_database_with_parameter_group(
    app, stack, environment_parameters, postgres_instance_parameters
):
    from aws_cdk import aws_rds as _rds

    keycloak_engine_version = _rds.DatabaseClusterEngine.aurora_postgres(
        version=_rds.AuroraPostgresEngineVersion.VER_12_8
    )

    parameter_group = _rds.ParameterGroup(
        scope=stack,
        id='test-parameter-group',
        engine=keycloak_engine_version,
        parameters=dict(
            max_prepared_transactions='5', timezone='Europe/Paris'
        ),
    )
    postgres_instance_parameters['parameter_group'] = parameter_group
    Database(**postgres_instance_parameters)

    template = Template.from_stack(stack)
    rendered_parameter_group = template.find_resources(
        'AWS::RDS::DBParameterGroup',
        {
            'Properties': {
                'Description': 'Parameter '
                'group '
                'for '
                'aurora-postgresql12',
                'Family': 'aurora-postgresql12',
                'Parameters': {
                    'max_prepared_transactions': '5',
                    'timezone': 'Europe/Paris',
                },
            }
        },
    )
    rendered_parameter_group_id = list(rendered_parameter_group.keys())[0]
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'DBParameterGroupName': {'Ref': rendered_parameter_group_id}},
    )


def test_database_with_database_instance_parameters_group_name(
    app, stack, environment_parameters, postgres_instance_parameters
):
    postgres_instance_parameters[
        'database_cluster_parameters_group_name'
    ] = 'test-parameter-group'
    Database(**postgres_instance_parameters)

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'DBParameterGroupName': 'test-parameter-group'},
    )


def test_database_with_database_cluster_parameters_group_name(
    app, stack, environment_parameters, aurora_cluster_parameters
):
    aurora_cluster_parameters[
        'database_cluster_parameters_group_name'
    ] = 'default.aurora.group.name'
    Database(**aurora_cluster_parameters)

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {'DBClusterParameterGroupName': 'default.aurora.group.name'},
    )


def test_database_with_database_cluster_parameters_group_name_from_engine(
    app, stack, environment_parameters, aurora_cluster_parameters
):
    Database(**aurora_cluster_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {'DBClusterParameterGroupName': 'default.aurora-mysql5.7'},
    )


@pytest.mark.parametrize(
    'database_parameters,cdk_type',
    [
        ('aurora_cluster_parameters', 'AWS::RDS::DBCluster'),
        ('postgres_instance_parameters', 'AWS::RDS::DBInstance'),
    ],
)
def test_deletion_protection(
    app, stack, environment_parameters, database_parameters, cdk_type, request
):
    db_params = request.getfixturevalue(database_parameters)
    db_params['environment'] = 'Production'
    Database(**db_params)

    template = Template.from_stack(stack)
    template.has_resource_properties(cdk_type, {'DeletionProtection': True})


@pytest.mark.parametrize(
    'database_parameters,cdk_type',
    [
        ('aurora_cluster_parameters', 'AWS::RDS::DBCluster'),
        ('postgres_instance_parameters', 'AWS::RDS::DBInstance'),
    ],
)
def test_deletion_protection_disabled_development(
    app, stack, environment_parameters, database_parameters, cdk_type, request
):
    db_params = request.getfixturevalue(database_parameters)
    db_params['environment'] = 'Development'
    Database(**db_params)

    template = Template.from_stack(stack)
    template.has_resource_properties(
        cdk_type, Match.not_({'DeletionProtection': True})
    )


@pytest.mark.parametrize(
    'environment,count', [('Development', 1), ('Production', 2)]
)
def test_database_cluster_has_ha_only_in_production(
    app,
    stack,
    environment_parameters,
    environment,
    count,
    aurora_cluster_parameters,
):
    aurora_cluster_parameters['environment'] = environment
    Database(**aurora_cluster_parameters)

    template = Template.from_stack(stack)
    template.resource_count_is('AWS::RDS::DBInstance', count)


def test_database_cluster_default_parameters(
    app, stack, environment_parameters, aurora_cluster_parameters
):
    Database(**aurora_cluster_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {
            'BackupRetentionPeriod': 30,
            'PreferredBackupWindow': '01:00-02:00',
            'PreferredMaintenanceWindow': 'mon:03:00-mon:04:00',
            'DatabaseName': 'fao_default_schema',
        },
    )


def test_database_instance_default_parameters(
    app, stack, environment_parameters, postgres_instance_parameters
):
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {
            'BackupRetentionPeriod': 30,
            'PreferredMaintenanceWindow': 'mon:03:00-mon:04:00',
        },
    )
    # 'DatabaseName': 'fao_default_schema'})


def test_database_cluster_export_s3_bucket(
    app, stack, environment_parameters, aurora_cluster_parameters
):
    bucket1 = aws_cdk.aws_s3.Bucket(stack, 'bucket1', bucket_name='bucket1')
    aurora_cluster_parameters['s3_export_buckets'] = [bucket1]
    Database(**aurora_cluster_parameters)

    template = Template.from_stack(stack)
    roles = template.find_resources('AWS::IAM::Role')
    role_id = [
        key
        for key in roles.keys()
        if key.startswith('testdatabaseidclusterS3ExportRole')
    ][0]
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {'AssociatedRoles': [{'RoleArn': {'Fn::GetAtt': [role_id, 'Arn']}}]},
    )


def test_database_cluster_import_s3_bucket(
    app, stack, environment_parameters, aurora_cluster_parameters
):
    bucket1 = aws_cdk.aws_s3.Bucket(stack, 'bucket1', bucket_name='bucket1')
    aurora_cluster_parameters['s3_import_buckets'] = [bucket1]
    Database(**aurora_cluster_parameters)

    template = Template.from_stack(stack)
    roles = template.find_resources('AWS::IAM::Role')
    role_id = [
        key
        for key in roles.keys()
        if key.startswith('testdatabaseidclusterS3ImportRole')
    ][0]
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {'AssociatedRoles': [{'RoleArn': {'Fn::GetAtt': [role_id, 'Arn']}}]},
    )


@pytest.mark.parametrize(
    'database_parameters,cdk_type',
    [
        ('aurora_cluster_parameters', 'AWS::RDS::DBCluster'),
        ('postgres_instance_parameters', 'AWS::RDS::DBInstance'),
    ],
)
def test_database_instance_and_cluster_rotates_user(
    app, stack, environment_parameters, database_parameters, cdk_type, request
):
    db_params = request.getfixturevalue(database_parameters)
    Database(**db_params)
    template = Template.from_stack(stack)
    rotator = template.find_resources('AWS::Serverless::Application')
    rotator_id = list(rotator.keys())[0]
    secret_attachment = template.find_resources(
        'AWS::SecretsManager::SecretTargetAttachment'
    )
    secret_attachment_id = list(secret_attachment.keys())[0]

    template.has_resource_properties(
        'AWS::SecretsManager::RotationSchedule',
        {
            'RotationLambdaARN': {
                'Fn::GetAtt': [rotator_id, 'Outputs.RotationLambdaARN']
            },
            'RotationRules': {'ScheduleExpression': 'rate(30 days)'},
            'SecretId': {'Ref': secret_attachment_id},
        },
    )


@pytest.mark.parametrize(
    'database_parameters,cdk_type',
    [
        ('aurora_cluster_parameters', 'AWS::RDS::DBCluster'),
        ('postgres_instance_parameters', 'AWS::RDS::DBInstance'),
    ],
)
def test_database_cluster_and_instance_creates_dns_not_production(
    app, stack, environment_parameters, database_parameters, cdk_type, request
):
    db_params = request.getfixturevalue(database_parameters)
    db_params['create_dns'] = 'true'
    Database(**db_params)

    template = Template.from_stack(stack)
    database = template.find_resources(cdk_type)
    database_id = list(database.keys())[0]
    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {
            'HostedZoneId': '00000000000000000000000000000000',
            'Name': 'db.test-app.foo.bar.org.',
            'ResourceRecords': [
                {'Fn::GetAtt': [database_id, 'Endpoint.Address']}
            ],
            'TTL': '1800',
            'Type': 'CNAME',
        },
    )


@pytest.mark.parametrize(
    'database_parameters,cdk_type,snapshot_key',
    [
        (
            'aurora_cluster_parameters',
            'AWS::RDS::DBCluster',
            'SnapshotIdentifier',
        ),
        (
            'postgres_instance_parameters',
            'AWS::RDS::DBInstance',
            'DBSnapshotIdentifier',
        ),
    ],
)
def test_database_cluster_and_instance_creates_from_snapshot(
    app,
    stack,
    environment_parameters,
    database_parameters,
    cdk_type,
    snapshot_key,
    request,
):
    db_params = request.getfixturevalue(database_parameters)
    db_params['database_snapshot_id'] = 'some-snapshot-id'
    Database(**db_params)

    template = Template.from_stack(stack)
    template.has_resource_properties(
        cdk_type, {snapshot_key: 'some-snapshot-id'}
    )
    template.has_resource_properties(
        cdk_type, Match.not_({'MasterUsername': {}})
    )


@pytest.mark.parametrize(
    'database_parameters,cdk_type',
    [
        ('aurora_cluster_parameters', 'AWS::RDS::DBCluster'),
        ('postgres_instance_parameters', 'AWS::RDS::DBInstance'),
    ],
)
def test_database_cluster_and_instance_has_tag_scheduler(
    app, stack, environment_parameters, database_parameters, cdk_type, request
):
    db_params = request.getfixturevalue(database_parameters)
    db_params['tag_scheduler_uptime_skip'] = 'true'
    db_params['tag_scheduler_uptime'] = '08:00-18:00'
    db_params['tag_scheduler_uptime_days'] = '1-2-3-4-5'
    Database(**db_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        cdk_type,
        {
            'Tags': Match.array_with(
                [
                    {'Key': 'SchedulerSkip', 'Value': 'true'},
                    {'Key': 'SchedulerUptime', 'Value': '08:00-18:00'},
                    {'Key': 'SchedulerUptimeDays', 'Value': '1-2-3-4-5'},
                ]
            )
        },
    )


def test_database_instance_audit_logs(
    app, stack, environment_parameters, postgres_instance_parameters
):
    postgres_instance_parameters['cloudwatch_audit_log'] = 'true'
    postgres_instance_parameters['environment'] = 'Production'
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'EnableCloudwatchLogsExports': Match.array_with(['audit'])},
    )


def test_database_cluster_audit_logs(
    app, stack, environment_parameters, aurora_cluster_parameters
):
    aurora_cluster_parameters['cloudwatch_audit_log'] = 'true'
    aurora_cluster_parameters['environment'] = 'Production'
    Database(**aurora_cluster_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {'EnableCloudwatchLogsExports': Match.array_with(['audit'])},
    )


def test_database_oracle_default_license_is_include(
    app, stack, environment_parameters, oracle_instance_parameters
):
    Database(**oracle_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance', {'LicenseModel': 'license-included'}
    )


def test_database_oracle_license_is_byol(
    app, stack, environment_parameters, oracle_instance_parameters
):
    oracle_instance_parameters['oracle_license_is_byol'] = 'true'
    Database(**oracle_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance', {'LicenseModel': 'bring-your-own-license'}
    )


def test_database_oracle_oem_sg_is_attached(
    app, stack, environment_parameters, oracle_instance_parameters
):
    Database(**oracle_instance_parameters)
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'VPCSecurityGroups': Match.array_with(['sg-oracleoem'])},
    )


@pytest.mark.skip(reason='Cannot find the resource in the template')
def test_cloudwatch_audit_log(
    app, stack, environment_parameters, postgres_instance_parameters
):
    postgres_instance_parameters['cloudwatch_audit_log'] = 'true'
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    # Cannot find the cloudwatch audit in the template


def test_database_sqlserver_default_License_is_included(
    app, stack, environment_parameters, sqlserver_ex_instance_parameters
):
    Database(**sqlserver_ex_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance', {'LicenseModel': 'license-included'}
    )


def test_database_sqlserver_ex_is_single_az(
    app, stack, environment_parameters, sqlserver_ex_instance_parameters
):
    Database(**sqlserver_ex_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance', {'MultiAZ': False}
    )


def test_database_sqlserver_se_is_not_multi_az_in_development(
    app, stack, environment_parameters, sqlserver_ex_instance_parameters
):
    sqlserver_ex_instance_parameters['database_engine'] = 'sqlserver-se'
    sqlserver_ex_instance_parameters['database_engine_version'] = '12.4'
    Database(**sqlserver_ex_instance_parameters)
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::RDS::DBInstance', {'MultiAZ': False}
    )


def test_database_sqlserver_se_is_multi_az_in_production(
    app, stack, environment_parameters, sqlserver_ex_instance_parameters
):
    sqlserver_ex_instance_parameters['database_engine'] = 'sqlserver-se'
    sqlserver_ex_instance_parameters['database_engine_version'] = '12.4'
    sqlserver_ex_instance_parameters['environment'] = 'Production'
    Database(**sqlserver_ex_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties('AWS::RDS::DBInstance', {'MultiAZ': True})


@pytest.mark.parametrize('backup_enabled', ['true', 'false'])
def test_database_instance_has_rubrik_tags(
    app,
    stack,
    environment_parameters,
    postgres_instance_parameters,
    backup_enabled,
):
    postgres_instance_parameters['rubrik_backup'] = backup_enabled
    Database(**postgres_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {
            'Tags': Match.array_with(
                [{'Key': 'RubrikBackup', 'Value': backup_enabled}]
            )
        },
    )


def test_database_return_new_dashboard(
    app, stack, environment_parameters, postgres_instance_parameters
):
    db = Database(**postgres_instance_parameters)
    db._get_dashboard()
    template = Template.from_stack(stack)
    template.resource_count_is('AWS::CloudWatch::Dashboard', 1)


def test_database_return_already_existing_dashboard(
    app, stack, environment_parameters, postgres_instance_parameters
):
    db = Database(**postgres_instance_parameters)
    dashboard = db._create_dashboard()
    assert dashboard == db._get_dashboard()
    template = Template.from_stack(stack)
    template.resource_count_is('AWS::CloudWatch::Dashboard', 1)


@pytest.mark.parametrize(
    'database_parameters',
    ['aurora_cluster_parameters', 'postgres_instance_parameters'],
)
def test_database_render_widgets_creates_dashboard_with_widgets(
    app, stack, environment_parameters, database_parameters, request
):
    db_params = request.getfixturevalue(database_parameters)
    db = Database(**db_params)
    db.render_widgets()
    template = Template.from_stack(stack)
    template.resource_count_is('AWS::CloudWatch::Dashboard', 1)


def test_security_group_property(postgres_instance_parameters):
    db = Database(**postgres_instance_parameters)
    sg = db.security_group
    assert sg == db._database_security_group
    assert isinstance(sg, aws_cdk.aws_ec2.SecurityGroup)


def test_cluster_property(aurora_cluster_parameters):
    db = Database(**aurora_cluster_parameters)
    assert db.cluster == db._cluster
    assert isinstance(db.cluster, aws_cdk.aws_rds.DatabaseCluster)


def test_instance_property(postgres_instance_parameters):
    db = Database(**postgres_instance_parameters)
    assert db.instance == db._instance
    assert isinstance(db.instance, aws_cdk.aws_rds.DatabaseInstance)


def test_database_sqlserver_se_has_import_bucket_integration(
    app, stack, environment_parameters, sqlserver_se_instance_parameters
):
    import_bucket = Bucket(
        stack,
        'import-bucket',
        app_name='test',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name=f'import.dev.fao.org',
    )

    params = sqlserver_se_instance_parameters.copy()
    params['s3_export_buckets'] = [import_bucket.bucket]
    params['s3_import_buckets'] = [import_bucket.bucket]

    Database(**params)
    template = Template.from_stack(stack)
    iam_role = template.find_resources('AWS::IAM::Role')
    # Using index=1 as first IAM Role (index=0) is relative to the lambda to auto delete objects on bucket deletion
    iam_role_id = list(iam_role.keys())[1]

    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {
            'AssociatedRoles': Match.array_with(
                [
                    {
                        'FeatureName': 'S3_INTEGRATION',
                        'RoleArn': {'Fn::GetAtt': [iam_role_id, 'Arn']},
                    },
                ]
            )
        },
    )


def test_cluster_identifier(stack, aurora_cluster_parameters):
    Database(**aurora_cluster_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {'DBClusterIdentifier': 'test-app-development-aurora-mysql'},
    )


def test_cluster_identifier_with_postfix(stack, aurora_cluster_parameters):
    postfix = 'custom'
    params = aurora_cluster_parameters.copy()
    params['database_identifier_postfix'] = postfix
    Database(**params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBCluster',
        {'DBClusterIdentifier': 'test-app-custom-development-aurora-mysql'},
    )


def test_instance_identifier(stack, sqlserver_ex_instance_parameters):
    Database(**sqlserver_ex_instance_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'DBInstanceIdentifier': 'test-app-development-db'},
    )


def test_instance_identifier_with_postfix(
    stack, sqlserver_ex_instance_parameters
):
    postfix = 'custom'
    params = sqlserver_ex_instance_parameters.copy()
    params['database_identifier_postfix'] = postfix
    Database(**params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::RDS::DBInstance',
        {'DBInstanceIdentifier': 'test-app-custom-development-db'},
    )


def test_graph_database_cluster_identifier(
    app, stack, database_graph_default_parameters
):
    Database(**database_graph_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBCluster',
        {'DBClusterIdentifier': 'test-app-neptune-development-cluster'},
    )


def test_graph_database_cluster_default_engine_version(
    app, stack, database_graph_default_parameters
):
    Database(**database_graph_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBCluster',
        {
            'EngineVersion': '1.2.1.0',
        },
    )


def test_graph_database_cluster_storage_encrypted(
    app, stack, database_graph_default_parameters
):
    Database(**database_graph_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBCluster',
        {'StorageEncrypted': True},
    )


def test_graph_database_has_mandatory_tags(
    app, stack, environment_parameters, database_graph_default_parameters
):
    Database(**database_graph_default_parameters)
    from aws_cdk_constructs.utils import get_version

    version = get_version()
    mandatory_tags = {
        'Tags': Match.array_with(
            [
                {'Key': 'ApplicationName', 'Value': 'test-app'},
                {'Key': 'Environment', 'Value': 'Development'},
                {'Key': 'fao-cdk', 'Value': 'true'},
                {'Key': 'fao-cdk-construct', 'Value': 'database'},
                {'Key': 'fao-cdk-version', 'Value': version},
            ]
        )
    }
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBInstance', mandatory_tags
    )
    template.has_resource_properties(
        'AWS::Neptune::DBSubnetGroup', mandatory_tags
    )


def test_graph_database_deletion_protection(
    app, stack, environment_parameters, request
):
    db_params = request.getfixturevalue('database_graph_default_parameters')
    db_params['environment'] = 'Production'
    Database(**db_params)

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBCluster', {'DeletionProtection': True}
    )


def test_graph_database_instance_class(
    app, stack, environment_parameters, database_graph_default_parameters
):
    Database(**database_graph_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBInstance',
        {'DBInstanceClass': 'db.t4g.medium'},
    )


def test_graph_database_instance_identifier(
    app, stack, environment_parameters, database_graph_default_parameters
):
    Database(**database_graph_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBInstance',
        {'DBInstanceIdentifier': 'test-app-neptune-development-1'},
    )


def test_graph_database_instance_auto_minor_versions_upgrade(
    app, stack, environment_parameters, database_graph_default_parameters
):
    Database(**database_graph_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Neptune::DBInstance',
        {'AutoMinorVersionUpgrade': False},
    )


def test_documentdb_database_cluster_identifier(
    app, stack, database_documentdb_default_parameters
):
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DocDB::DBCluster',
        {'DBClusterIdentifier': 'test-app-documentdb-development-cluster'},
    )


def test_documentdb_database_cluster_storage_encrypted(
    app, stack, database_documentdb_default_parameters
):
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DocDB::DBCluster',
        {'StorageEncrypted': True},
    )


def test_documentdb_database_has_mandatory_tags(
    app, stack, environment_parameters, database_documentdb_default_parameters
):
    Database(**database_documentdb_default_parameters)
    from aws_cdk_constructs.utils import get_version

    version = get_version()
    mandatory_tags = {
        'Tags': Match.array_with(
            [
                {'Key': 'ApplicationName', 'Value': 'test-app'},
                {'Key': 'Environment', 'Value': 'Development'},
                {'Key': 'fao-cdk', 'Value': 'true'},
                {'Key': 'fao-cdk-construct', 'Value': 'database'},
                {'Key': 'fao-cdk-version', 'Value': version},
            ]
        )
    }
    template = Template.from_stack(stack)
    template.has_resource_properties('AWS::DocDB::DBInstance', mandatory_tags)
    template.has_resource_properties(
        'AWS::DocDB::DBSubnetGroup', mandatory_tags
    )


@pytest.mark.parametrize(
    'environment,deletion_protection',
    [('development', False), ('production', True)],
)
def test_documentdb_database_deletion_protection(
    app,
    stack,
    environment_parameters,
    database_documentdb_default_parameters,
    environment,
    deletion_protection,
):
    database_documentdb_default_parameters['environment'] = environment
    Database(**database_documentdb_default_parameters)

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DocDB::DBCluster', {'DeletionProtection': deletion_protection}
    )


def test_documentdb_database_instance_class(
    app, stack, environment_parameters, database_documentdb_default_parameters
):
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DocDB::DBInstance',
        {'DBInstanceClass': 'db.t4g.medium'},
    )


def test_documentdb_database_instance_identifier(
    app, stack, environment_parameters, database_documentdb_default_parameters
):
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DocDB::DBInstance',
        {
            'DBInstanceIdentifier': 'test-app-documentdb-development-clusterinstance1'
        },
    )


def test_documentdb_creates_dns_on_flag(
    app, stack, environment_parameters, database_documentdb_default_parameters
):
    database_documentdb_default_parameters['environment'] = 'development'
    database_documentdb_default_parameters['create_dns'] = 'true'
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {'Name': 'db.test-app-documentdb.foo.bar.org.'},
    )


@pytest.mark.parametrize(
    'env,flag', [('development', 'false'), ('production', 'true')]
)
def test_documentdb_skips_dns(
    app,
    stack,
    environment_parameters,
    database_documentdb_default_parameters,
    env,
    flag,
):
    database_documentdb_default_parameters['environment'] = env
    database_documentdb_default_parameters['create_dns'] = flag
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.resource_count_is('AWS::Route53::RecordSet', 0)


def test_documentdb_default_backup_and_maintenance_windows(
    app, stack, environment_parameters, database_documentdb_default_parameters
):
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DocDB::DBCluster',
        {
            'BackupRetentionPeriod': 30,
            'PreferredBackupWindow': '01:00-02:00',
            'PreferredMaintenanceWindow': 'mon:03:00-mon:04:00',
        },
    )


def test_documentdb_number_of_instances(
    app, stack, environment_parameters, database_documentdb_default_parameters
):
    database_documentdb_default_parameters['number_of_instances'] = 2
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)

    template.resource_count_is('AWS::DocDB::DBInstance', 2)


from aws_cdk_constructs.database import DocumentDBEngines


@pytest.mark.parametrize(
    'engine_version,engine,parameter_group_name',
    [
        (DocumentDBEngines.v3_0_0, '3.0.0', 'default.docdb3.0'),
        (DocumentDBEngines.v4_0_0, '4.0.0', 'default.docdb4.0'),
        (DocumentDBEngines.v5_0_0, '5.0.0', 'default.docdb5.0'),
    ],
)
def test_documentdb_engine_version_sets_correct_paramenter_group(
    app,
    stack,
    environment_parameters,
    database_documentdb_default_parameters,
    engine_version,
    engine,
    parameter_group_name,
):
    database_documentdb_default_parameters[
        'database_engine_version'
    ] = engine_version
    Database(**database_documentdb_default_parameters)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::DocDB::DBCluster',
        {
            'EngineVersion': engine,
            'DBClusterParameterGroupName': parameter_group_name,
        },
    )
