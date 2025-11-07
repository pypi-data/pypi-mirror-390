from aws_cdk.assertions import Template

from aws_cdk_constructs import Nlb


def test_creates_nlb_with_correct_properties(
    stack, vpc, environment_parameters
):
    Nlb(
        stack,
        'testnlb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        main_component_name='foo',
        environments_parameters=environment_parameters,
        network_load_balancer_subnet_2='subnet-00000002',
        network_load_balancer_subnet_1='subnet-00000001',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='2.2.2.2',
        ec2_traffic_port='8888',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'Scheme': 'internal',
            'SubnetMappings': [
                {
                    'PrivateIPv4Address': '1.1.1.1',
                    'SubnetId': 'subnet-00000001',
                },
                {
                    'PrivateIPv4Address': '2.2.2.2',
                    'SubnetId': 'subnet-00000002',
                },
            ],
            'Type': 'network',
            'LoadBalancerAttributes': [
                {'Key': 'deletion_protection.enabled', 'Value': 'true'},
                {'Key': 'load_balancing.cross_zone.enabled', 'Value': 'true'},
            ],
        },
    )


def test_creates_tg_with_correct_properties(
    stack, vpc, environment_parameters
):
    Nlb(
        stack,
        'testnlb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        main_component_name='foo',
        environments_parameters=environment_parameters,
        network_load_balancer_subnet_2='subnet-00000002',
        network_load_balancer_subnet_1='subnet-00000001',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='2.2.2.2',
        ec2_traffic_port='8888',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {
            'HealthCheckIntervalSeconds': 30,
            'HealthCheckPort': '8888',
            'HealthCheckProtocol': 'TCP',
            'HealthCheckTimeoutSeconds': 10,
            'HealthyThresholdCount': 2,
            'Port': 8888,
            'Protocol': 'TCP',
            'Tags': [
                {'Key': 'ApplicationName', 'Value': 'app_name'},
                {'Key': 'Environment', 'Value': 'Production'},
            ],
            'TargetType': 'instance',
            'UnhealthyThresholdCount': 2,
        },
    )


def test_creates_nlb_with_custom_healthcheck(
    stack, vpc, environment_parameters
):
    Nlb(
        stack,
        'testnlb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        main_component_name='foo',
        environments_parameters=environment_parameters,
        network_load_balancer_subnet_2='subnet-00000002',
        network_load_balancer_subnet_1='subnet-00000001',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='2.2.2.2',
        ec2_traffic_port='8888',
        healthy_threshold_count=5,
        unhealthy_threshold_count=5,
        interval=10,
        timeout=10,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {
            'HealthCheckIntervalSeconds': 10,
            'HealthCheckPort': '8888',
            'HealthCheckProtocol': 'TCP',
            'HealthCheckTimeoutSeconds': 10,
            'HealthyThresholdCount': 5,
            'Port': 8888,
            'Protocol': 'TCP',
            'Tags': [
                {'Key': 'ApplicationName', 'Value': 'app_name'},
                {'Key': 'Environment', 'Value': 'Production'},
            ],
            'TargetType': 'instance',
            'UnhealthyThresholdCount': 5,
        },
    )


def test_creates_listener(stack, vpc, environment_parameters):
    Nlb(
        stack,
        'testnlb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        main_component_name='foo',
        environments_parameters=environment_parameters,
        network_load_balancer_subnet_2='subnet-00000002',
        network_load_balancer_subnet_1='subnet-00000001',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='2.2.2.2',
        ec2_traffic_port='8888',
    )
    template = Template.from_stack(stack)

    tg = template.find_resources('AWS::ElasticLoadBalancingV2::TargetGroup')
    tg_id = list(tg.keys())[0]
    lb = template.find_resources('AWS::ElasticLoadBalancingV2::LoadBalancer')
    lb_id = list(lb.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {'TargetGroupArn': {'Ref': tg_id}, 'Type': 'forward'}
            ],
            'LoadBalancerArn': {'Ref': lb_id},
            'Port': 8888,
            'Protocol': 'TCP',
        },
    )


def test_creates_dns_record(stack, vpc, environment_parameters):
    Nlb(
        stack,
        'testnlb',
        app_name='app_name',
        environment='Development',
        vpc=vpc,
        main_component_name='foo',
        environments_parameters=environment_parameters,
        network_load_balancer_subnet_2='subnet-00000002',
        network_load_balancer_subnet_1='subnet-00000001',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='2.2.2.2',
        ec2_traffic_port='8888',
        create_dns='true',
    )

    template = Template.from_stack(stack)
    nlb = template.find_resources('AWS::ElasticLoadBalancingV2::LoadBalancer')
    nlb_id = list(nlb.keys())[0]

    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {
            'Name': 'app_name.foo.bar.org.',
            'Type': 'A',
            'AliasTarget': {
                'DNSName': {
                    'Fn::Join': [
                        '',
                        ['dualstack.', {'Fn::GetAtt': [nlb_id, 'DNSName']}],
                    ]
                },
                'HostedZoneId': {
                    'Fn::GetAtt': [nlb_id, 'CanonicalHostedZoneID']
                },
            },
            'HostedZoneId': '00000000000000000000000000000000',
        },
    )


def test_nlb_with_load_balancer_name(stack, vpc, environment_parameters):
    Nlb(
        stack,
        'testnlb',
        app_name='app_name',
        load_balancer_name='testname',
        environment='Production',
        vpc=vpc,
        main_component_name='foo',
        environments_parameters=environment_parameters,
        network_load_balancer_subnet_2='subnet-00000002',
        network_load_balancer_subnet_1='subnet-00000001',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='2.2.2.2',
        ec2_traffic_port='8888',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer', {'Name': 'testname'}
    )


def test_nlb_without_name_uses_id(stack, vpc, environment_parameters):
    Nlb(
        stack,
        'testnlb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        main_component_name='foo',
        environments_parameters=environment_parameters,
        network_load_balancer_subnet_2='subnet-00000002',
        network_load_balancer_subnet_1='subnet-00000001',
        network_load_balancer_ip_1='1.1.1.1',
        network_load_balancer_ip_2='2.2.2.2',
        ec2_traffic_port='8888',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer', {'Name': 'testnlb'}
    )
