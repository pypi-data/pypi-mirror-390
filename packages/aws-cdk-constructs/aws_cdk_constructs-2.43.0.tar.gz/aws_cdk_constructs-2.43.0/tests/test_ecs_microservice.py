import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template, Match

from aws_cdk_constructs.ecs.cluster import ECSCluster
from aws_cdk_constructs.ecs.microservice import ECSMicroservice
from aws_cdk_constructs.efs.volume import EFSVolume


@pytest.fixture
def app():
    return cdk.App()


@pytest.fixture
def stack(app):
    env = cdk.Environment(account='123456789012', region='eu-west-1')
    return cdk.Stack(app, 'test-stack', env=env)


@pytest.fixture
def vpc(stack):
    return cdk.aws_ec2.Vpc(stack, 'test-vpc')


@pytest.fixture
def cluster(stack, vpc, mocker, environment_parameters):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    return ECSCluster(
        scope=stack,
        id='x',
        environments_parameters=environment_parameters,
        environment='development',
        app_name='test-app',
    )


@pytest.fixture
def cluster_ec2(stack, vpc, mocker, environment_parameters):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    return ECSCluster(
        scope=stack,
        id='x',
        environments_parameters=environment_parameters,
        environment='development',
        app_name='test-app',
        ec2_enable=True,
        ec2_instance_type='t2.micro',
        ec2_max_capacity=1,
        ec2_desired_capacity=1,
    )


@pytest.fixture
def template(stack, ms):
    return Template.from_stack(stack)


@pytest.fixture
def ms(stack, cluster):
    return ECSMicroservice(
        scope=stack, name='test-ms', image='repository/image', cluster=cluster
    )


@pytest.fixture
def ms_ec2(stack, cluster_ec2):
    return ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster_ec2,
        deploy_to_ec2=True,
    )


def test_construct_default_values(stack, cluster, ms):
    assert ms.id == 'test-ms'
    assert ms.image == 'repository/image'
    assert ms.image_tag == 'master'
    assert ms.container_env is None
    assert ms.cpu == 256
    assert ms.memory_limit_mib == 512
    assert ms.entry_point is None
    assert ms.vpc == cluster.vpc
    assert ms.cluster == cluster
    assert ms.port == 80
    assert ms.health_check_path == '/'
    assert ms.hostname == 'test-ms-test-app.example.com'
    assert ms.desired_count == 1
    assert ms.max_count is None
    assert ms.min_count is None
    assert ms.cpu_threshold is None
    assert ms.log_driver_blocking_mode is False
    assert ms.max_buffer_size_mib == 4
    assert len(ms.security_groups) == 1
    assert isinstance(ms.security_groups[0], cdk.aws_ec2.SecurityGroup)


def test_template_has_microservice(template):
    template.resource_count_is('AWS::ECS::Service', 1)


def test_ms_builds_cname(stack, vpc, environment_parameters, mocker):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    hosted_zone = cdk.aws_route53.HostedZone(
        stack, 'zone-id', zone_name='example.com'
    )
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environments_parameters=environment_parameters,
        environment='development',
        hosted_zone=hosted_zone,
        app_name='test-app',
    )
    ms = ECSMicroservice(
        scope=stack, name='test-ms', image='repository/image', cluster=cluster
    )

    assert isinstance(ms.cname, cdk.aws_route53.CnameRecord)
    template = Template.from_stack(stack)
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'test-stack-alb'}},
    )
    alb_id = list(alb.keys())[0]

    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {
            'Name': 'test-ms-test-app.example.com.',
            'Type': 'CNAME',
            'ResourceRecords': [{'Fn::GetAtt': [alb_id, 'DNSName']}],
        },
    )


def test_ms_builds_default_sg(template):
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupDescription': 'test-stack/test-ms-sg',
            'SecurityGroupEgress': [{'CidrIp': '0.0.0.0/0'}],
        },
    )


def test_ms_builds_service(template):
    template.has_resource_properties(
        'AWS::ECS::Service',
        {
            'DesiredCount': 1,
            'LaunchType': 'FARGATE',
            'PropagateTags': 'SERVICE',
        },
    )


def test_ms_builds_task_definition(template):
    template.has_resource_properties(
        'AWS::ECS::TaskDefinition',
        {
            'ContainerDefinitions': [
                {
                    'Essential': True,
                    'Image': {
                        'Fn::Join': [
                            '',
                            [
                                '123456789012.dkr.ecr.eu-west-1.',
                                {'Ref': 'AWS::URLSuffix'},
                                '/repository/image:master',
                            ],
                        ]
                    },
                    'LogConfiguration': {
                        'LogDriver': 'awslogs',
                        'Options': {
                            'awslogs-stream-prefix': 'test-ms-main-container',
                            'mode': 'non-blocking',
                            'max-buffer-size': '4194304b',
                        },
                    },
                    'Name': 'test-ms-main-container',
                    'PortMappings': [{'ContainerPort': 80, 'Protocol': 'tcp'}],
                }
            ],
            'Cpu': '256',
            'Memory': '512',
            'NetworkMode': 'awsvpc',
            'RequiresCompatibilities': ['FARGATE'],
        },
    )


def test_ms_custom_fields(stack, vpc, mocker, environment_parameters):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    hosted_zone = cdk.aws_route53.HostedZone(
        stack, 'zone-id', zone_name='custom.org'
    )
    sg = cdk.aws_ec2.SecurityGroup(
        stack,
        'SecurityGroup',
        vpc=vpc,
        description='Allow ssh access to ec2 instances',
        allow_all_outbound=False,
    )
    sg.add_ingress_rule(
        cdk.aws_ec2.Peer.ipv4('1.2.3.4/32'),
        cdk.aws_ec2.Port.tcp(22),
        'allow ssh access from the world',
    )

    cluster = ECSCluster(
        scope=stack,
        id='x',
        environments_parameters=environment_parameters,
        environment='development',
        hosted_zone=hosted_zone,
        app_name='test-app',
        domain_name='custom.org',
    )
    ms = ECSMicroservice(
        scope=stack,
        name='custom-name',
        image='custom-repository/custom-image',
        image_tag='custom-tag',
        container_env={'one': 'two', 'three': '2'},
        cpu=2048,
        memory_limit_mib=4096,
        entry_point=['/usr/local/bin', 'entrypoint', '-param'],
        port=443,
        health_check_path='/healthcheck',
        cluster=cluster,
        desired_count=5,
        security_group=sg,
        health_check_timeout=10,
        unhealthy_threshold_count=10,
        healthy_threshold_count=10,
        health_check_interval=60,
        max_buffer_size_mib=8,
    )

    template = Template.from_stack(stack)
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'test-stack-alb'}},
    )
    alb_id = list(alb.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'SecurityGroupIngress': [
                {'CidrIp': '1.2.3.4/32', 'ToPort': 22, 'IpProtocol': 'tcp'}
            ]
        },
    )
    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {
            'Name': 'custom-name-test-app.custom.org.',
            'ResourceRecords': [{'Fn::GetAtt': [alb_id, 'DNSName']}],
        },
    )
    template.has_resource_properties(
        'AWS::ECS::Service',
        {
            'DesiredCount': 5,
            'LoadBalancers': [
                {
                    'ContainerName': 'custom-name-main-container',
                    'ContainerPort': 443,
                }
            ],
        },
    )
    template.has_resource_properties(
        'AWS::ECS::TaskDefinition',
        {
            'ContainerDefinitions': [
                {
                    'EntryPoint': ['/usr/local/bin', 'entrypoint', '-param'],
                    'Environment': [
                        {'Name': 'one', 'Value': 'two'},
                        {'Name': 'three', 'Value': '2'},
                    ],
                    'Image': {
                        'Fn::Join': [
                            '',
                            [
                                '123456789012.dkr.ecr.eu-west-1.',
                                {'Ref': 'AWS::URLSuffix'},
                                '/custom-repository/custom-image:custom-tag',
                            ],
                        ]
                    },
                    'LogConfiguration': {
                        'LogDriver': 'awslogs',
                        'Options': {
                            'awslogs-stream-prefix': 'custom-name-main-container',
                            'mode': 'non-blocking',
                            'max-buffer-size': '8388608b',
                        },
                    },
                    'PortMappings': [
                        {'ContainerPort': 443, 'Protocol': 'tcp'}
                    ],
                }
            ],
            'Cpu': '2048',
            'Memory': '4096',
        },
    )
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {
            'HealthCheckPath': '/healthcheck',
            'HealthCheckPort': '443',
            'Port': 443,
            'Protocol': 'HTTP',
            'HealthCheckIntervalSeconds': 60,
            'HealthCheckTimeoutSeconds': 10,
            'HealthyThresholdCount': 10,
            'UnhealthyThresholdCount': 10,
        },
    )
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::ListenerRule',
        {
            'Actions': [{'Type': 'forward'}],
            'Conditions': [
                {
                    'Field': 'host-header',
                    'HostHeaderConfig': {
                        'Values': ['custom-name-test-app.custom.org']
                    },
                }
            ],
        },
    )


def test_send_mails(stack, cluster):
    ms = ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        sends_emails=True,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ECS::Service',
        {
            'NetworkConfiguration': {
                'AwsvpcConfiguration': {
                    'SecurityGroups': [{}, 'smtp-relay-sg-id']
                }
            }
        },
    )


def test_ms_with_autoscaling(stack, cluster):
    ms = ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        max_count=10,
        min_count=1,
        cpu_threshold=50,
    )

    assert ms.max_count == 10
    assert ms.min_count == 1
    assert ms.cpu_threshold == 50

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ApplicationAutoScaling::ScalableTarget',
        {'MaxCapacity': 10, 'MinCapacity': 1},
    )
    template.has_resource_properties(
        'AWS::ApplicationAutoScaling::ScalingPolicy',
        {'TargetTrackingScalingPolicyConfiguration': {'TargetValue': 50}},
    )


def test_attach_volume(stack, ms, environment_parameters):
    ms.attach_volume(name='volume-name', mount_point='/mount/point')
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ECS::TaskDefinition',
        {
            'ContainerDefinitions': [
                {
                    'MountPoints': [
                        {
                            'ContainerPath': '/mount/point',
                            'SourceVolume': 'volume-name',
                        }
                    ]
                }
            ],
            'Volumes': [{'Name': 'volume-name'}],
        },
    )

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress', {'ToPort': 2049}
    )


def test_add_init_container(stack, ms, vpc, environment_parameters):
    volume = EFSVolume(
        scope=stack,
        id='test-volume',
        vpc=vpc,
        volume_mount_path='/somepath',
        environment='development',
        environments_parameters=environment_parameters,
        app_name='app-name',
    )
    ms.add_init_container(
        name='test-init-container',
        volume=volume,
        dockerfile_path='/tests/dummy_path'
        # name="test-init-container", volume=volume, dockerfile_path="/dummy_path"
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ECS::TaskDefinition',
        {
            'ContainerDefinitions': [
                {
                    'DependsOn': [
                        {
                            'Condition': 'SUCCESS',
                            'ContainerName': 'test-ms-test-init-container-init-container',
                        }
                    ],
                    'Essential': True,
                },
                {
                    'Essential': False,
                    'MountPoints': [
                        {
                            'ContainerPath': '/dst_dir',
                            'SourceVolume': 'test-volume',
                        }
                    ],
                    'Name': 'test-ms-test-init-container-init-container',
                },
            ]
        },
    )


def test_create_cname(stack, ms):
    hosted_zone = cdk.aws_route53.HostedZone(
        stack, 'zone-id', zone_name='example.com'
    )
    ms.create_cname(hosted_zone)
    template = Template.from_stack(stack)
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'test-stack-alb'}},
    )

    alb_id = list(alb.keys())[0]
    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {
            'Name': 'test-ms-test-app.example.com.',
            'ResourceRecords': [{'Fn::GetAtt': [alb_id, 'DNSName']}],
            'Type': 'CNAME',
        },
    )


def test_service_has_desired_count_tag(stack, ms, template):
    template.has_resource_properties(
        'AWS::ECS::Service',
        {
            'Tags': Match.array_with(
                [{'Key': 'SchedulerDesiredCount', 'Value': '1'}]
            )
        },
    )


def test_service_has_default_scheduling_tags(stack, ms, template):
    template.has_resource_properties(
        'AWS::ECS::Service',
        {
            'Tags': Match.array_with(
                [
                    {'Key': 'SchedulerSkip', 'Value': 'false'},
                    {'Key': 'SchedulerUptime', 'Value': '08:00-18:00'},
                    {'Key': 'SchedulerUptimeDays', 'Value': '1-2-3-4-5'},
                ]
            )
        },
    )


def test_incorrect_cpu_mem_combination_raises_exception(stack, cluster):
    with pytest.raises(ValueError):
        ECSMicroservice(
            scope=stack,
            name='test-ms',
            image='repository/image',
            cluster=cluster,
            cpu=512,
            memory_limit_mib=512,
            desired_count=1,
        )


def test_service_has_custom_scheduling_tags(stack, cluster):
    ms = ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        desired_count=1,
        tag_scheduler_uptime_skip='true',
        tag_scheduler_uptime='09:00-17:00',
        tag_scheduler_uptime_days='1-3-5-7',
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ECS::Service',
        {
            'Tags': Match.array_with(
                [
                    {'Key': 'SchedulerSkip', 'Value': 'true'},
                    {'Key': 'SchedulerUptime', 'Value': '09:00-17:00'},
                    {'Key': 'SchedulerUptimeDays', 'Value': '1-3-5-7'},
                ]
            )
        },
    )


def test_service_includes_all_alternative_fqdns(
    stack, vpc, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    hosted_zone = cdk.aws_route53.HostedZone(
        stack, 'zone-id', zone_name='example.com'
    )
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environments_parameters=environment_parameters,
        environment='development',
        hosted_zone=hosted_zone,
        app_name='test-app',
    )
    ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        alternative_fqdns=['test-app.example.com', 'app.example.com'],
    )
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::ListenerRule',
        {
            'Actions': [{'Type': 'forward'}],
            'Conditions': [
                {
                    'Field': 'host-header',
                    'HostHeaderConfig': {
                        'Values': ['test-ms-test-app.example.com']
                    },
                }
            ],
        },
    )
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::ListenerRule',
        {
            'Actions': [{'Type': 'forward'}],
            'Conditions': [
                {
                    'Field': 'host-header',
                    'HostHeaderConfig': {'Values': ['test-app.example.com']},
                }
            ],
        },
    )
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::ListenerRule',
        {
            'Actions': [{'Type': 'forward'}],
            'Conditions': [
                {
                    'Field': 'host-header',
                    'HostHeaderConfig': {'Values': ['app.example.com']},
                }
            ],
        },
    )


def test_service_empty_alternative_fqdns(
    stack, vpc, environment_parameters, mocker
):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)
    hosted_zone = cdk.aws_route53.HostedZone(
        stack, 'zone-id', zone_name='example.com'
    )
    cluster = ECSCluster(
        scope=stack,
        id='x',
        environments_parameters=environment_parameters,
        environment='development',
        hosted_zone=hosted_zone,
        app_name='test-app',
    )
    ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        alternative_fqdns=[],
    )
    template = Template.from_stack(stack)
    template.resource_count_is('AWS::ElasticLoadBalancingV2::ListenerRule', 1)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::ListenerRule',
        {
            'Actions': [{'Type': 'forward'}],
            'Conditions': [
                {
                    'Field': 'host-header',
                    'HostHeaderConfig': {
                        'Values': ['test-ms-test-app.example.com']
                    },
                }
            ],
        },
    )


def test_ms_log_blocking_mode(stack, cluster):
    ms = ECSMicroservice(
        scope=stack,
        name='test-ms',
        image='repository/image',
        cluster=cluster,
        desired_count=1,
        log_driver_blocking_mode=True,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ECS::TaskDefinition',
        {
            'ContainerDefinitions': [
                {
                    'LogConfiguration': {
                        'LogDriver': 'awslogs',
                        'Options': {
                            'awslogs-stream-prefix': 'test-ms-main-container',
                            'mode': 'blocking',
                        },
                    },
                }
            ],
        },
    )


def test_ms_on_ec2_has_autoassigend_port_on_targetgroup(
    stack, cluster_ec2, ms_ec2
):
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {'Port': 80, 'TargetType': 'instance'},
    )


def test_ms_on_ec2_adds_sg_from_ec2_to_alb(stack, cluster_ec2, ms_ec2):
    template = Template.from_stack(stack)
    srv_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupDescription': 'test-stack/x/test-app-sg'}},
    )

    srv_sg_id = list(srv_sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {'SourceSecurityGroupId': {'Fn::GetAtt': [srv_sg_id, 'GroupId']}},
    )


def test_ms_has_launch_type_ec2(stack, cluster_ec2, ms_ec2):
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ECS::Service', {'LaunchType': 'EC2'}
    )
