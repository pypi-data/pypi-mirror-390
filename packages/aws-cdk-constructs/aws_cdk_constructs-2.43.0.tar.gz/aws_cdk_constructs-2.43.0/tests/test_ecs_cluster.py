from os import environ

import aws_cdk as cdk
from aws_cdk.assertions import Template, Match

from aws_cdk_constructs import ECSCluster, ECSMicroservice
import pytest


def test_creates_ecs_cluster_template(
    stack, hosted_zone, environment_parameters, mocker
):
    mocker.patch(
        'aws_cdk.aws_ec2.Vpc.from_lookup',
        return_value=cdk.aws_ec2.Vpc(stack, 'test-vpc'),
    )

    ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        hosted_zone=hosted_zone,
        app_name='testapp',
    )

    template = Template.from_stack(stack)
    template.resource_count_is('AWS::ECS::Cluster', 1)


def test_ecs_cluster_default_values(
    stack, hosted_zone, environment_parameters, mocker
):
    vpc = cdk.aws_ec2.Vpc(stack, 'text-vpc')
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        hosted_zone=hosted_zone,
        app_name='testapp',
    )

    assert isinstance(cluster.cluster, cdk.aws_ecs.Cluster)
    assert cluster.domain_name == 'example.com'
    assert cluster.hosted_zone == hosted_zone
    assert cluster.id == 'x'
    assert len(cluster.microservices) == 0
    assert cluster.vpc == vpc


def test_ecs_cluster_values(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        domain_name='newone.com',
        hosted_zone=hosted_zone,
    )

    assert cluster.domain_name == 'newone.com'


def test_ecs_cluster_creates_alb(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        domain_name='newone.com',
        hosted_zone=hosted_zone,
    )
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': [
                {'Key': 'deletion_protection.enabled', 'Value': 'false'},
                {'Key': 'idle_timeout.timeout_seconds', 'Value': '50'},
                {'Key': 'access_logs.s3.enabled', 'Value': 'true'},
                {'Key': 'access_logs.s3.bucket', 'Value': 'fao-elb-logs'},
                {'Key': 'access_logs.s3.prefix', 'Value': 'testapp'},
            ],
            'Name': 'teststack-alb',
            'Scheme': 'internal',
            'Type': 'application',
        },
    )


def test_ecs_cluster_creates_alb_with_custom_idle(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        domain_name='newone.com',
        load_balancer_idle_timeout=600,
        hosted_zone=hosted_zone,
    )
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': [
                {'Key': 'deletion_protection.enabled', 'Value': 'false'},
                {'Key': 'idle_timeout.timeout_seconds', 'Value': '600'},
                {'Key': 'access_logs.s3.enabled', 'Value': 'true'},
                {'Key': 'access_logs.s3.bucket', 'Value': 'fao-elb-logs'},
                {'Key': 'access_logs.s3.prefix', 'Value': 'testapp'},
            ],
            'Name': 'teststack-alb',
            'Scheme': 'internal',
            'Type': 'application',
        },
    )


def test_ecs_cluster_creates_alb_without_invalid_headers(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        domain_name='newone.com',
        hosted_zone=hosted_zone,
        will_drop_invalid_headers='true',
    )
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': [
                {'Key': 'deletion_protection.enabled', 'Value': 'false'},
                {'Key': 'idle_timeout.timeout_seconds', 'Value': '50'},
                {
                    'Key': 'routing.http.drop_invalid_header_fields.enabled',
                    'Value': 'true',
                },
                {'Key': 'access_logs.s3.enabled', 'Value': 'true'},
                {'Key': 'access_logs.s3.bucket', 'Value': 'fao-elb-logs'},
                {'Key': 'access_logs.s3.prefix', 'Value': 'testapp'},
            ],
            'Name': 'teststack-alb',
            'Scheme': 'internal',
            'Type': 'application',
        },
    )


def test_ecs_cluster_microservices_list(
    stack, vpc, hosted_zone, mocker, environment_parameters
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
    )

    microservice = mocker.MagicMock()
    cluster.register_ms(microservice)

    assert len(cluster.microservices) == 1


def test_ecs_cluster_listener_rule_priority_no_stored_params(
    stack, vpc, hosted_zone, mocker, environment_parameters
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    environ['AWS_ACCESS_KEY_ID'] = 'nope'
    environ['AWS_SECRET_ACCESS_KEY'] = 'nope'
    environ['AWS_SESSION_TOKEN'] = 'nope'
    environ['AWS_DEFAULT_REGION'] = 'eu-west-1'

    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
    )
    from botocore.stub import Stubber

    cluster.alb._initialize_ssm_client()
    st = Stubber(cluster.alb._client)
    st.add_client_error('get_parameter')
    st.activate()
    ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::ListenerRule', {'Priority': 200}
    )


@pytest.mark.parametrize(
    'stored_priority,cf_priority', [(101, 1), (100, 1), (1, 100)]
)
def test_ecs_cluster_listener_rule_priority_stored_param(
    stack,
    vpc,
    hosted_zone,
    mocker,
    environment_parameters,
    stored_priority,
    cf_priority,
):
    from botocore.stub import Stubber

    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    environ['AWS_ACCESS_KEY_ID'] = 'nope'
    environ['AWS_SECRET_ACCESS_KEY'] = 'nope'
    environ['AWS_SESSION_TOKEN'] = 'nope'
    environ['AWS_DEFAULT_REGION'] = 'eu-west-1'

    response = {
        'Parameter': {
            'Name': '/statsuite/statsuite-public-cluster-iac-alb/rule_priority',
            'Type': 'String',
            'Value': f'{stored_priority}',
            'Version': 2,
            'LastModifiedDate': '2023-08-21T14:59:45.633000+02:00',
            'ARN': 'arn:aws:ssm:eu-west-1:674129056020:parameter/statsuite/statsuite-public-cluster-iac-alb/rule_priority',
            'DataType': 'text',
        }
    }
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
    )
    cluster.alb._initialize_ssm_client()
    st = Stubber(cluster.alb._client)
    st.add_response('get_parameter', response)
    st.activate()
    ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
    )
    st.deactivate()
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::ListenerRule', {'Priority': cf_priority}
    )


def test_ecs_cluster_public_facing(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        internet_facing=True,
    )
    ms = ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'testapp_teststack_alb_sg',
            'SecurityGroupIngress': Match.array_with(
                [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Everyone',
                        'FromPort': 443,
                        'IpProtocol': 'tcp',
                        'ToPort': 443,
                    }
                ]
            ),
        },
    )


def test_cluster_creates_dashboard(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        track=True,
    )

    assert cluster.dashboard is not None


import pytest


@pytest.mark.parametrize('alb, count', [(True, 1), (False, 0)])
def test_cluster_creates_alb(
    stack, vpc, hosted_zone, environment_parameters, mocker, alb, count
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        create_alb=alb,
    )

    template = Template.from_stack(stack)
    template.resource_count_is(
        'AWS::ElasticLoadBalancingV2::LoadBalancer', count
    )


def test_cluster_return_new_dashboard(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
    )
    cluster._get_dashboard()
    template = Template.from_stack(stack)
    template.resource_count_is('AWS::CloudWatch::Dashboard', 1)


def test_cluster_return_already_existing_dashboard(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
    )
    dashboard = cluster._create_dashboard()
    assert dashboard == cluster._get_dashboard()
    template = Template.from_stack(stack)
    template.resource_count_is('AWS::CloudWatch::Dashboard', 1)


def test_cluster_render_widgets_in_dashbaord(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
    )
    cluster.render_widgets()
    template = Template.from_stack(stack)
    dashboard = template.find_resources('AWS::CloudWatch::Dashboard')
    dashboard_id = list(dashboard.keys())[0]
    widgets = (
        dashboard.get(dashboard_id)
        .get('Properties')
        .get('DashboardBody')
        .get('Fn::Join')[1]
    )
    assert len(widgets) == 17


def test_cluster_render_widgets_from_microservides(
    stack, vpc, hosted_zone, mocker, environment_parameters
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        target_priority=100,
    )
    ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
    )
    ECSMicroservice(
        scope=stack,
        name='test-msx',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
    )

    cluster.render_widgets()
    template = Template.from_stack(stack)
    dashboard = template.find_resources('AWS::CloudWatch::Dashboard')
    dashboard_id = list(dashboard.keys())[0]
    widgets = (
        dashboard.get(dashboard_id)
        .get('Properties')
        .get('DashboardBody')
        .get('Fn::Join')[1]
    )
    assert len(widgets) == 137


def test_cluster_render_widgets_from_microservices_internal_are_ignored(
    stack, vpc, hosted_zone, mocker, environment_parameters
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        target_priority=100,
    )
    ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
    )
    ECSMicroservice(
        scope=stack,
        name='test-msx',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
        internal=True,
    )

    cluster.render_widgets()
    template = Template.from_stack(stack)
    dashboard = template.find_resources('AWS::CloudWatch::Dashboard')
    dashboard_id = list(dashboard.keys())[0]
    widgets = (
        dashboard.get(dashboard_id)
        .get('Properties')
        .get('DashboardBody')
        .get('Fn::Join')[1]
    )
    assert len(widgets) == 97


def test_ecs_requires_all_ec2_params_to_be_enables(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        target_priority=100,
        ec2_enable=True,
        ec2_instance_type='t2.micro',
        ec2_max_capacity=1,
    )

    assert cluster.ec2_enabled == False


def test_ecs_with_ec2_creates_sg_with_port_range(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        target_priority=100,
        ec2_enable=True,
        ec2_instance_type='t2.micro',
        ec2_max_capacity=1,
        ec2_desired_capacity=1,
    )
    template = Template.from_stack(stack)
    alb_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupName': f'testapp_{stack.stack_name}_alb_sg',
            }
        },
    )
    alb_sg_id = list(alb_sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'FromPort': 32768,
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
            'ToPort': 65535,
        },
    )


def test_ecs_with_ec2_creates_right_launch_template(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    secret = cdk.aws_secretsmanager.Secret(
        stack,
        'Secret',
        secret_object_value={
            'production/ami_id': cdk.SecretValue.unsafe_plain_text(
                'ami_id_response'
            )
        },
    )
    mocker.patch(
        'aws_cdk.aws_secretsmanager.Secret.from_secret_complete_arn',
        return_value=secret,
    )
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        target_priority=100,
        ec2_enable=True,
        ec2_instance_type='t2.micro',
        ec2_max_capacity=1,
        ec2_desired_capacity=1,
    )

    template = Template.from_stack(stack)
    secret = template.find_resources(
        'AWS::SecretsManager::Secret',
        {
            'Properties': {
                'SecretString': '{"production/ami_id":"ami_id_response"}'
            }
        },
    )
    secret_id = list(secret.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::LaunchTemplate',
        {
            'LaunchTemplateData': {
                'ImageId': {
                    'Fn::Join': [
                        '',
                        [
                            '{{resolve:secretsmanager:',
                            {'Ref': secret_id},
                            ':SecretString:production/ami_id::}}',
                        ],
                    ]
                },
                'InstanceType': 't2.micro',
            }
        },
    )


def test_ecs_with_ec2_creates_asg(
    stack, vpc, hosted_zone, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    cluster = ECSCluster(
        scope=stack,
        id='x',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='testapp',
        hosted_zone=hosted_zone,
        target_priority=100,
        ec2_enable=True,
        ec2_instance_type='t2.micro',
        ec2_max_capacity=1,
        ec2_desired_capacity=1,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::AutoScaling::AutoScalingGroup',
        {
            'DesiredCapacity': '1',
            'MaxSize': '1',
            'MinSize': '1',
            'Tags': [
                {
                    'Key': 'SchedulerSkip',
                    'PropagateAtLaunch': True,
                    'Value': 'False',
                },
                {
                    'Key': 'SchedulerUptime',
                    'PropagateAtLaunch': True,
                    'Value': '08:00-18:00',
                },
                {
                    'Key': 'SchedulerUptimeDays',
                    'PropagateAtLaunch': True,
                    'Value': '1-2-3-4-5',
                },
            ],
        },
    )
