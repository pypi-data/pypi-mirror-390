import aws_cdk as cdk
import aws_cdk.aws_iam
import pytest
from aws_cdk.assertions import Template, Match

from aws_cdk_constructs import Microservice, EFSVolume


@pytest.fixture
def app():
    return cdk.App()


@pytest.fixture
def stack(app):
    env = cdk.Environment(account='00000000001', region='eu-west-1')
    return cdk.Stack(app, 'teststack', env=env)


@pytest.fixture
def vpc(stack):
    return cdk.aws_ec2.Vpc(stack, 'testvpc')


@pytest.fixture
def sg(stack, vpc):
    return cdk.aws_ec2.SecurityGroup(
        stack,
        'SecurityGroup',
        vpc=vpc,
        description='Dummy security group',
        allow_all_outbound=False,
    )


@pytest.fixture
def asg(stack, vpc):
    return cdk.aws_autoscaling.AutoScalingGroup(
        stack,
        'AutoScalingGroup',
        vpc=vpc,
        machine_image=cdk.aws_ec2.AmazonLinuxImage(),
        instance_type=cdk.aws_ec2.InstanceType.of(
            cdk.aws_ec2.InstanceClass.BURSTABLE2,
            cdk.aws_ec2.InstanceSize.MICRO,
        ),
    )


@pytest.fixture
def ms_params(stack, environment_parameters):
    return {
        'scope': stack,
        'id': 'testms',
        'app_name': 'testapp',
        'environment': 'Development',
        'environments_parameters': environment_parameters,
        'main_component_name': 'testmaincomponent',
        'will_be_ha': False,
        'additional_variables': {},
        'traffic_port': '80',
        'ec2_traffic_port': '8000',
        'ec2_instance_type': 't3.small',
        'ec2_ami_id': 'LATEST',
    }


def test_microservice_creates_efs_volume(stack, environment_parameters):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Development',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::EFS::FileSystem',
        {
            'Encrypted': False,
            'FileSystemTags': Match.array_with(
                [{'Key': 'HasBackup', 'Value': 'false'}]
            ),
        },
    )

    template.has_resource('AWS::EFS::FileSystem', {'DeletionPolicy': 'Delete'})
    template.has_resource(
        'AWS::EFS::FileSystem', {'UpdateReplacePolicy': 'Delete'}
    )

    efs_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/{main_component_name}efs/EfsSecurityGroup'
            }
        },
    )

    template = Template.from_stack(stack)
    efs_sg_id = list(efs_sg.keys())[0]

    instance_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/{main_component_name}_ec2_secg'
            }
        },
    )

    instance_sg_id = list(instance_sg.keys())[0]

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'FromPort': 2049,
            'GroupId': {'Fn::GetAtt': [efs_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': {
                'Fn::GetAtt': [instance_sg_id, 'GroupId']
            },
            'ToPort': 2049,
        },
    )


def test_microservice_creates_volume_with_backup_in_production(
    stack, environment_parameters
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::EFS::FileSystem',
        {
            'Encrypted': False,
            'FileSystemTags': Match.array_with(
                [{'Key': 'HasBackup', 'Value': 'true'}]
            ),
        },
    )

    template.has_resource('AWS::EFS::FileSystem', {'DeletionPolicy': 'Retain'})
    template.has_resource(
        'AWS::EFS::FileSystem', {'UpdateReplacePolicy': 'Retain'}
    )

    efs_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/{main_component_name}efs/EfsSecurityGroup'
            }
        },
    )
    efs_sg_id = list(efs_sg.keys())[0]
    instance_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/{main_component_name}_ec2_secg'
            }
        },
    )
    instance_sg_id = list(instance_sg.keys())[0]

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'FromPort': 2049,
            'GroupId': {'Fn::GetAtt': [efs_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': {
                'Fn::GetAtt': [instance_sg_id, 'GroupId']
            },
            'ToPort': 2049,
        },
    )


def test_microservice_creates_volume_without_backup(
    stack, environment_parameters
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::EFS::FileSystem',
        {
            'FileSystemTags': Match.not_(
                [{'Key': 'HasBackup', 'Value': 'true'}]
            )
        },
    )


def test_microservice_attach_existing_efs_volume_by_security_group(
    stack, sg, environment_parameters
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        existing_efs_security_group=sg,
    )

    template = Template.from_stack(stack)
    provided_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupDescription': 'Dummy security group'}},
    )
    provided_sg_id = list(provided_sg.keys())[0]

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'FromPort': 2049,
            'GroupId': {'Fn::GetAtt': [provided_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'ToPort': 2049,
        },
    )


def test_microservice_attach_existing_efs_volume_by_security_group_without_backup(
    stack, sg, environment_parameters
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Development',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        existing_efs_security_group=sg,
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    provided_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupDescription': 'Dummy security group'}},
    )
    provided_sg_id = list(provided_sg.keys())[0]

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'FromPort': 2049,
            'GroupId': {'Fn::GetAtt': [provided_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'ToPort': 2049,
        },
    )


def test_microservice_creates_nlb(stack, environment_parameters, asg):
    main_component_name = 'testmaincomponent'
    Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='1.1.1.2',
        network_load_balancer_subnet_1='1.1.1.0/24',
        network_load_balancer_subnet_2='1.1.2.0/24',
        network_load_balancer_source_autoscaling_group=asg,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': [
                {'Key': 'deletion_protection.enabled', 'Value': 'true'},
                {'Key': 'load_balancing.cross_zone.enabled', 'Value': 'true'},
            ],
            'Scheme': 'internal',
            'SubnetMappings': [
                {'PrivateIPv4Address': '1.1.1.1', 'SubnetId': '1.1.1.0/24'},
                {'PrivateIPv4Address': '1.1.1.2', 'SubnetId': '1.1.2.0/24'},
            ],
            'Type': 'network',
        },
    )

    nlb_arn = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Type': 'network'}},
    )
    nlb_arn_id = list(nlb_arn.keys())[0]
    tg_nlb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {'Properties': {'TargetType': 'instance', 'VpcId': 'vpcid'}},
    )
    tb_nlb_id = list(tg_nlb.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {'TargetGroupArn': {'Ref': tb_nlb_id}, 'Type': 'forward'}
            ],
            'LoadBalancerArn': {'Ref': nlb_arn_id},
            'Port': 8000,
            'Protocol': 'TCP',
        },
    )
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {
            'HealthCheckIntervalSeconds': 30,
            'HealthCheckPort': '8000',
            'HealthCheckProtocol': 'TCP',
            'HealthyThresholdCount': 2,
            'Port': 8000,
            'Protocol': 'TCP',
            'TargetType': 'instance',
            'UnhealthyThresholdCount': 2,
            'VpcId': 'vpcid',
        },
    )


def test_microservice_raises_exception_on_partially_defined_nl(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    try:
        Microservice(
            scope=stack,
            id='testms',
            app_name='testapp',
            environment='Production',
            environments_parameters=environment_parameters,
            main_component_name=main_component_name,
            will_be_ha=False,
            will_use_efs='true',
            additional_variables={},
            traffic_port='80',
            ec2_traffic_port='8000',
            ec2_instance_type='t3.small',
            ec2_ami_id='LATEST',
            rubrik_backup='false',
            network_load_balancer_ip_2='1.1.1.2',
            network_load_balancer_subnet_1='1.1.1.0/24',
            network_load_balancer_subnet_2='1.1.2.0/24',
            network_load_balancer_source_autoscaling_group=asg,
        )
    except Exception as e:
        assert e.args == (
            'Network load balancer needs the following parameters: network_load_balancer_ip_1, network_load_balancer_ip_2, network_load_balancer_subnet_1, network_load_balancer_subnet_2, network_load_balancer_source_autoscaling_group',
        )


def test_microservice_creates_alb(stack, environment_parameters, asg):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    alb_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/alb-fao-construct/testapp-teststack_testms-sg'
            }
        },
    )

    alb_sg_id = list(alb_sg.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': [
                {'Key': 'deletion_protection.enabled', 'Value': 'true'},
                {'Key': 'idle_timeout.timeout_seconds', 'Value': '50'},
                {'Key': 'access_logs.s3.enabled', 'Value': 'true'},
                {'Key': 'access_logs.s3.bucket', 'Value': 'fao-elb-logs'},
                {'Key': 'access_logs.s3.prefix', 'Value': 'testapp'},
            ],
            'Name': 'testapp-testmaincomponent-alb',
            'SecurityGroups': [
                {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
                'some-sg',
            ],
            'Scheme': 'internal',
            'Subnets': ['subnet-00000003', 'subnet-00000004'],
            'Type': 'application',
        },
    )
    alb_tg = template.find_resources(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {'Properties': {'Name': f'testapp-{main_component_name}-8000'}},
    )

    alb_tg_id = list(alb_tg.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {'TargetGroupArn': {'Ref': alb_tg_id}, 'Type': 'forward'}
            ],
            'LoadBalancerArn': {'Ref': 'testmsalb8A8BD17B'},
            'Port': 80,
            'Protocol': 'HTTP',
        },
    )

    ec2_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/{main_component_name}_ec2_secg'
            }
        },
    )
    # Security group from lb to instance
    ec2_sg_id = list(ec2_sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Load ' 'balancer ' 'to ' 'target',
            'FromPort': 8000,
            'GroupId': {'Fn::GetAtt': [ec2_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
            'ToPort': 8000,
        },
    )


def test_microservice_is_private_creates_alb_with_access_from_fao(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_be_public='false',
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Type': 'application'},
    )
    alb_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/alb-fao-construct/testapp-teststack_testms-sg'
            }
        },
    )
    alb_sg_id = list(alb_sg.keys())[0]

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Prefix ' 'list ' 'FAO ' 'Clients',
            'FromPort': 80,
            'GroupId': {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000001',
            'ToPort': 80,
        },
    )


def test_microservice_creates_public_alb_with_no_upstream_and_no_cdn(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_be_public='true',
        will_use_cdn='false',
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Type': 'application'},
    )

    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupDescription': 'teststack/testms/alb-fao-construct/testapp-teststack_testms-sg',
            'GroupName': 'testapp_teststack_testms_alb_sg',
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
            'SecurityGroupIngress': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Everyone',
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'ToPort': 80,
                }
            ],
            'VpcId': 'vpcid',
        },
    )


def test_microservice_creates_public_alb_with_access_from_upstream(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_be_public='true',
        upstream_security_group='sg-upstream',
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Type': 'application'},
    )
    alb_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/alb-fao-construct/testapp-teststack_testms-sg'
            }
        },
    )
    alb_sg_id = list(alb_sg.keys())[0]

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'From ' 'upstream',
            'FromPort': 80,
            'GroupId': {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': 'sg-upstream',
            'ToPort': 80,
        },
    )


def test_microservice_creates_private_alb_with_https(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        ssl_certificate_arn='ssl-arn',
        will_be_public='false',
        upstream_security_group='sg-upstream',
        will_use_efs='true',
        additional_variables={},
        traffic_port='443',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Type': 'application'},
    )
    alb_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/alb-fao-construct/testapp-teststack_testms-sg'
            }
        },
    )
    alb_sg_id = list(alb_sg.keys())[0]

    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Prefix ' 'list ' 'FAO ' 'Clients',
            'FromPort': 80,
            'GroupId': {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000001',
            'ToPort': 80,
        },
    )

    alb_arn = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testapp-testmaincomponent-alb'}},
    )
    alb_arn_id = list(alb_arn.keys())[0]

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {
                    'RedirectConfig': {
                        'Host': '#{host}',
                        'Path': '/#{path}',
                        'Port': '443',
                        'Protocol': 'HTTPS',
                        'Query': '#{query}',
                        'StatusCode': 'HTTP_301',
                    },
                    'Type': 'redirect',
                }
            ],
            'LoadBalancerArn': {'Ref': alb_arn_id},
            'Port': 80,
            'Protocol': 'HTTP',
        },
    )


def test_microservice_creates_public_alb_with_no_upstream_no_cdn_and_https(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_be_public='true',
        will_use_cdn='false',
        ssl_certificate_arn='ssl-arn',
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Type': 'application'},
    )

    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupDescription': 'teststack/testms/alb-fao-construct/testapp-teststack_testms-sg',
            'GroupName': 'testapp_teststack_testms_alb_sg',
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
            'SecurityGroupIngress': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Everyone to HTTP',
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'ToPort': 80,
                }
            ],
            'VpcId': 'vpcid',
        },
    )


def test_microservices_creates_alb_is_private_and_has_upstream(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        upstream_security_group='sg-upstream',
        will_be_public='false',
        will_use_cdn='false',
        ssl_certificate_arn='ssl-arn',
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Type': 'application'},
    )
    alb_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/alb-fao-construct/testapp-teststack_testms-sg'
            }
        },
    )
    alb_sg_id = list(alb_sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'From ' 'upstream',
            'FromPort': 80,
            'GroupId': {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': 'sg-upstream',
            'ToPort': 80,
        },
    )


def test_microservice_creates_alb_is_not_production(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Development',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        upstream_security_group='sg-upstream',
        will_be_public='false',
        will_use_cdn='false',
        ssl_certificate_arn='ssl-arn',
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'SecurityGroupIngress': [
                {
                    'CidrIp': '168.202.4.57/32',
                    'Description': 'From ' 'Security ' 'Scan ' 'tool',
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'ToPort': 80,
                }
            ],
        },
    )

    # has_oicd


def test_microservice_creates_alb_with_oicd(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Development',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        authorization_endpoint='http://auth',
        token_endpoint='token',
        issuer='issuer',
        client_id='client_id',
        client_secret='client_secret',
        user_info_endpoint='user_info_endpoint',
        will_be_ha=False,
        ssl_certificate_arn='certificate',
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    alb_arn = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testapp-testmaincomponent-alb'}},
    )
    alb_arn_id = list(alb_arn.keys())[0]

    tg = template.find_resources(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {'Properties': {'Name': 'testapp-testmaincomponent-8000'}},
    )
    tg_id = list(tg.keys())[0]

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'Certificates': [{'CertificateArn': 'certificate'}],
            'DefaultActions': [
                {
                    'AuthenticateOidcConfig': {
                        'AuthorizationEndpoint': 'http://auth',
                        'ClientId': 'client_id',
                        'ClientSecret': 'client_secret',
                        'Issuer': 'issuer',
                        'TokenEndpoint': 'token',
                        'UserInfoEndpoint': 'user_info_endpoint',
                    },
                    'Order': 1,
                    'Type': 'authenticate-oidc',
                },
                {
                    'Order': 2,
                    'TargetGroupArn': {'Ref': tg_id},
                    'Type': 'forward',
                },
            ],
            'LoadBalancerArn': {'Ref': alb_arn_id},
            'Port': 80,
            'Protocol': 'HTTPS',
            'SslPolicy': 'ELBSecurityPolicy-FS-1-2-Res-2019-08',
        },
    )


def test_microservice_creates_alb_without_invalid_header_fields(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
        will_drop_invalid_headers='true',
    )

    template = Template.from_stack(stack)
    alb_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {
            'Properties': {
                'GroupDescription': f'{stack.stack_name}/{ms.id}/alb-fao-construct/testapp-teststack_testms-sg'
            }
        },
    )

    alb_sg_id = list(alb_sg.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': [
                {'Key': 'deletion_protection.enabled', 'Value': 'true'},
                {'Key': 'idle_timeout.timeout_seconds', 'Value': '50'},
                {
                    'Key': 'routing.http.drop_invalid_header_fields.enabled',
                    'Value': 'true',
                },
                {'Key': 'access_logs.s3.enabled', 'Value': 'true'},
                {'Key': 'access_logs.s3.bucket', 'Value': 'fao-elb-logs'},
                {'Key': 'access_logs.s3.prefix', 'Value': 'testapp'},
            ],
            'Name': 'testapp-testmaincomponent-alb',
            'SecurityGroups': [
                {'Fn::GetAtt': [alb_sg_id, 'GroupId']},
                'some-sg',
            ],
            'Scheme': 'internal',
            'Subnets': ['subnet-00000003', 'subnet-00000004'],
            'Type': 'application',
        },
    )


def test_microservice_raises_exception_with_incomplete_oicd(
    stack, environment_parameters, asg
):
    main_component_name = 'testmaincomponent'
    try:
        Microservice(
            scope=stack,
            id='testms',
            app_name='testapp',
            environment='Development',
            environments_parameters=environment_parameters,
            main_component_name=main_component_name,
            authorization_endpoint='http://auth',
            issuer='issuer',
            client_id='client_id',
            client_secret='client_secret',
            user_info_endpoint='user_info_endpoint',
            will_be_ha=False,
            ssl_certificate_arn='certificate',
            will_use_efs='true',
            additional_variables={},
            traffic_port='80',
            ec2_traffic_port='8000',
            ec2_instance_type='t3.small',
            ec2_ami_id='LATEST',
            rubrik_backup='false',
        )
    except Exception as e:
        assert e.args == (
            'OIDC configuration is not valid! If you aimed to configure OIDC listener please provide each of the params: authorization_endpoint, token_endpoint, issuer, client_id, client_secret, user_info_endpoint',
        )


def test_microservice_get_ec2_role(stack, ms_params):
    ms = Microservice(**ms_params)
    role = ms.ec2_role
    assert role.to_string() == 'teststack/testms/asg_role'
    assert isinstance(role, aws_cdk.aws_iam.Role)


def test_microservice_get_vpc(stack, ms_params):
    ms = Microservice(**ms_params)
    ms_vpc = ms.vpc
    assert ms_vpc.to_string() == 'teststack/testms/VPC'


def test_microservice_get_alb_logs_bucket(stack, ms_params):
    ms = Microservice(**ms_params)
    bucket = ms.alb_logs_bucket
    assert (
        bucket.to_string()
        == 'teststack/testms/alb-fao-construct/alb_logs_bucket'
    )


def test_microservice_get_tcp_connection_ec2_traffic_port(stack, ms_params):
    ms = Microservice(**ms_params)
    tcp_connection = ms.tcp_connection_ec2_traffic_port
    assert tcp_connection.to_string() == '8000'
    assert isinstance(tcp_connection, aws_cdk.aws_ec2.Port)


def test_microservice_get_tcp_connection_traffic_port(stack, ms_params):
    ms = Microservice(**ms_params)
    tcp_connection = ms.tcp_connection_traffic_port
    assert tcp_connection.to_string() == '80'
    assert isinstance(tcp_connection, aws_cdk.aws_ec2.Port)


def test_microservice_get_target_group(stack, ms_params):
    ms = Microservice(**ms_params)
    tg = ms.target_group
    assert (
        tg.to_string()
        == 'teststack/testms/alb-fao-construct/testmaincomponent_alb_tg'
    )
    assert isinstance(
        tg, aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup
    )


def test_microservice_get_auto_scaling_group(stack, ms_params):
    ms = Microservice(**ms_params)
    asg = ms.auto_scaling_group
    assert asg.to_string() == 'teststack/testms/asg'
    assert isinstance(asg, aws_cdk.aws_autoscaling.AutoScalingGroup)


def test_microservice_get_network_load_balancer(stack, ms_params, asg):
    ms_params['network_load_balancer_ip_1'] = '1.1.1.1'
    ms_params['network_load_balancer_ip_2'] = '1.1.1.2'
    ms_params['network_load_balancer_subnet_1'] = '1.1.1.0/24'
    ms_params['network_load_balancer_subnet_2'] = '1.1.2.0/24'
    ms_params['network_load_balancer_source_autoscaling_group'] = asg
    ms = Microservice(**ms_params)
    nlb = ms.network_load_balancer
    assert nlb.to_string() == 'teststack/testms/nlb_nlb'
    assert isinstance(
        nlb, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer
    )


def test_microservice_get_load_balancer(stack, ms_params):
    ms = Microservice(**ms_params)
    lb = ms.load_balancer
    assert lb.to_string() == 'teststack/testms/alb'
    assert isinstance(
        lb, aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer
    )


def test_microservice_get_load_balancer_security_group(stack, ms_params):
    ms = Microservice(**ms_params)
    sg = ms.load_balancer_security_group
    assert (
        sg.to_string()
        == 'teststack/testms/alb-fao-construct/testapp-teststack_testms-sg'
    )
    assert isinstance(sg, aws_cdk.aws_ec2.SecurityGroup)


def test_microservice_get_ec2_instance_security_group(stack, ms_params):
    ms = Microservice(**ms_params)
    sg = ms.ec2_instance_security_group
    assert sg.to_string() == 'teststack/testms/testmaincomponent_ec2_secg'
    assert isinstance(sg, aws_cdk.aws_ec2.SecurityGroup)


def test_microservice_get_user_data(stack, ms_params):
    ms = Microservice(**ms_params)
    user_data = ms.user_data
    user_data.startswith('#!/bin/bash')
    assert isinstance(user_data, str)


def test_microservice_get_efs(stack, ms_params):
    ms_params['will_use_efs'] = 'true'
    ms = Microservice(**ms_params)
    efs = ms.efs
    assert efs.to_string() == 'teststack/testms/testmaincomponentefs'
    assert isinstance(efs, aws_cdk.aws_efs.FileSystem)


def test_microservice_get_efs_security_group(stack, ms_params):
    ms_params['will_use_efs'] = 'true'
    ms = Microservice(**ms_params)
    sg = ms.efs_security_group
    assert (
        sg.to_string()
        == 'teststack/testms/testmaincomponentefs/EfsSecurityGroup'
    )
    assert isinstance(sg, aws_cdk.aws_ec2.SecurityGroup)


def test_microservice_get_efs_construct(stack, ms_params):
    ms_params['will_use_efs'] = 'true'
    ms = Microservice(**ms_params)
    efs_construct = ms.get_efs_construct()
    assert (
        efs_construct.to_string()
        == 'teststack/testms/testmaincomponent-efsvolumefromms'
    )
    assert isinstance(efs_construct, EFSVolume)


def test_microservice_enable_fao_private_access(stack, ms_params, sg):
    ms = Microservice(**ms_params)
    ms.enable_fao_private_access(sg)
    template = Template.from_stack(stack)
    rendered_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupDescription': 'Dummy security group'}},
    )
    sg_id = list(rendered_sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'SourcePrefixListId': 'pl-00000000000000001',
            'GroupId': {'Fn::GetAtt': [sg_id, 'GroupId']},
        },
    )


def test_microservice_create_security_group(stack, ms_params):
    ms = Microservice(**ms_params)
    sg = ms.create_security_group(
        scope=stack,
        id='testsg',
        app_name='testapp',
        environment='Development',
        security_group_name='sg-name',
    )
    assert isinstance(sg, aws_cdk.aws_ec2.SecurityGroup)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupDescription': 'teststack/testsg',
            'GroupName': 'sg-name',
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
        },
    )


def test_microservice_set_user_data_additional_variables(stack, ms_params):
    ms = Microservice(**ms_params)
    ms.set_user_data_additional_variables({'TEST_VAR': 'test_value'})
    user_data = ms.user_data
    assert 'export TEST_VAR=test_value' in user_data


def test_microservice_with_user_data_additional_variables_adds_them(
    stack, ms_params
):
    ms_params['additional_variables'] = {'TEST_VAR': 'test_value'}
    ms = Microservice(**ms_params)
    user_data = ms.user_data
    assert 'export TEST_VAR=test_value' in user_data


def test_microservice_asg_name(stack, ms_params):
    ms = Microservice(**ms_params)
    assert ms.asg_name() == 'asg'


def test_microservice_raises_exception_when_additional_variables_is_not_a_dict(
    stack, ms_params
):
    ms_params['additional_variables'] = 3

    try:
        Microservice(**ms_params)
    except Exception as e:
        assert (
            str(e)
            == 'additional_variables should be passed as a python dictionary'
        )


def test_microservice_creates_ebs(stack, ms_params):
    ms_params['ebs_volume_size'] = 10
    ms = Microservice(**ms_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::Volume',
        {
            'AvailabilityZone': 'eu-west-1',
            'Encrypted': True,
            'KmsKeyId': '00000000-0000-0000-0000-000000000002',
            'Size': 10,
            'VolumeType': 'gp3',
        },
    )


@pytest.mark.parametrize(
    'flag, has_backup', [(None, 'true'), ('True', 'true'), ('False', 'false')]
)
def test_microservice_ebs_has_backup(stack, ms_params, flag, has_backup):
    ms_params['ebs_volume_size'] = 10
    if flag is not None:
        ms_params['rubrik_backup'] = flag
    ms = Microservice(**ms_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::Volume',
        {
            'Tags': Match.array_with(
                [{'Key': 'RubrikBackup', 'Value': has_backup}]
            )
        },
    )


def test_microservice_attach_policy_to_assets_bucket(stack, ms_params):
    ms_params['s3_assets_bucket_name'] = 'assets-bucket-name'
    ms = Microservice(**ms_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::Policy',
        {
            'PolicyDocument': {
                'Statement': [
                    {
                        'Action': 's3:*',
                        'Effect': 'Allow',
                        'Resource': [
                            'arn:aws:s3:::assets-bucket-name',
                            'arn:aws:s3:::assets-bucket-name/*',
                        ],
                    }
                ],
                'Version': '2012-10-17',
            }
        },
    )


def test_microservice_attach_policy_to_code_bucket(stack, ms_params):
    ms_params['s3_code_bucket_name'] = 'code-bucket-name'
    ms = Microservice(**ms_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::Policy',
        {
            'PolicyDocument': {
                'Statement': [
                    {
                        'Action': 's3:*',
                        'Effect': 'Allow',
                        'Resource': [
                            'arn:aws:s3:::code-bucket-name',
                            'arn:aws:s3:::code-bucket-name/*',
                        ],
                    }
                ],
                'Version': '2012-10-17',
            }
        },
    )


@pytest.mark.parametrize(
    'flag, has_backup', [(None, 'true'), ('True', 'true'), ('False', 'false')]
)
def test_microservice_asg_has_backup_tags(stack, ms_params, flag, has_backup):
    if flag is not None:
        ms_params['rubrik_backup'] = flag
    ms = Microservice(**ms_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::AutoScaling::AutoScalingGroup',
        {
            'Tags': Match.array_with(
                [
                    {
                        'Key': 'RubrikBackup',
                        'PropagateAtLaunch': True,
                        'Value': has_backup,
                    }
                ]
            )
        },
    )


def test_microservice_asg_has_scheduler_tags(stack, ms_params):
    ms_params['tag_scheduler_uptime_skip'] = 'true'
    ms_params['tag_scheduler_uptime'] = '08:00-18:00'
    ms_params['tag_scheduler_uptime_days'] = '1-2-3-4-5'
    Microservice(**ms_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::AutoScaling::AutoScalingGroup',
        {
            'Tags': Match.array_with(
                [
                    {
                        'Key': 'SchedulerSkip',
                        'PropagateAtLaunch': True,
                        'Value': 'true',
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
                ]
            )
        },
    )


def test_microservice_asg_does_not_have_scheduler_tags_in_prod(
    stack, ms_params
):
    ms_params['environment'] = 'Production'
    ms_params['tag_scheduler_uptime_skip'] = 'true'
    ms_params['tag_scheduler_uptime'] = '08:00-18:00'
    ms_params['tag_scheduler_uptime_days'] = '1-2-3-4-5'
    Microservice(**ms_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::AutoScaling::AutoScalingGroup',
        {
            'Tags': Match.not_(
                [
                    {
                        'Key': 'SchedulerSkip',
                        'PropagateAtLaunch': True,
                        'Value': 'true',
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
                ]
            )
        },
    )


def test_microservice_with_downstream_adds_security_group(
    stack, ms_params, sg, mocker
):
    ms_params['downstream_security_group'] = 'some-sg-id'
    ms_params['downstream_port'] = 1234
    mocker.patch(
        'aws_cdk.aws_ec2.SecurityGroup.from_security_group_id', return_value=sg
    )

    Microservice(**ms_params)
    template = Template.from_stack(stack)

    rendered_sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupDescription': 'Dummy security group'}},
    )
    sg_id = list(rendered_sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'EC2 to downstream',
            'FromPort': 1234,
            'GroupId': {'Fn::GetAtt': [sg_id, 'GroupId']},
            'ToPort': 1234,
        },
    )


def test_microservice_creates_asg_with_default_grace_period(
    stack, environment_parameters
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::AutoScaling::AutoScalingGroup', {'HealthCheckGracePeriod': 600}
    )


@pytest.mark.parametrize(
    'param, result',
    [(cdk.Duration.minutes(1), 60), (cdk.Duration.seconds(5), 5)],
)
def test_microservice_creates_asg_with_grace_period(
    stack, environment_parameters, asg, param, result
):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
        asg_healthcheck_grace_period=param,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::AutoScaling::AutoScalingGroup',
        {'HealthCheckGracePeriod': result},
    )


def test_microservice_specific_os_distribution(stack, environment_parameters):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
        ec2_os_distribution='AMAZON_LINUX_2',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::EC2::LaunchTemplate',
        {
            'LaunchTemplateData': {
                'ImageId': '{{resolve:secretsmanager:arn:aws:secretsmanager:eu-west-1:000000000001:secret:imagebuilder-al2-x86-ami-secret-abc123:SecretString:production/ami_id::}}'
            }
        },
    )


def test_microservice_default_os_distribution(stack, environment_parameters):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::EC2::LaunchTemplate',
        {
            'LaunchTemplateData': {
                'ImageId': '{{resolve:secretsmanager:arn:aws:secretsmanager:eu-west-1:000000000001:secret:imagebuilder-al2023-x86-ami-secret-abc123:SecretString:production/ami_id::}}'
            }
        },
    )


def test_microservice_default_imdsv2(stack, environment_parameters):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::EC2::LaunchTemplate',
        {
            'LaunchTemplateData': {
                'MetadataOptions': {'HttpTokens': 'optional'}
            }
        },
    )


def test_microservice_with_imdsv2(stack, environment_parameters):
    main_component_name = 'testmaincomponent'
    ms = Microservice(
        scope=stack,
        id='testms',
        app_name='testapp',
        environment='Production',
        environments_parameters=environment_parameters,
        main_component_name=main_component_name,
        will_be_ha=False,
        will_use_efs='true',
        additional_variables={},
        traffic_port='80',
        ec2_traffic_port='8000',
        ec2_instance_type='t3.small',
        ec2_ami_id='LATEST',
        rubrik_backup='false',
        will_use_imdsv2='true',
    )

    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::EC2::LaunchTemplate',
        {
            'LaunchTemplateData': {
                'MetadataOptions': {'HttpTokens': 'required'}
            }
        },
    )
