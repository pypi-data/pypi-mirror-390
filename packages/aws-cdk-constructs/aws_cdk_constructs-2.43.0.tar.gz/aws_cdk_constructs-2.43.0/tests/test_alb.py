from aws_cdk.assertions import Template, Match

from aws_cdk_constructs import Alb


def test_alb_raises_exception_when_not_all_oicd_params_present(
    stack, vpc, environment_parameters
):
    try:
        Alb(
            stack,
            'testalb',
            app_name='app_name',
            environment='Production',
            vpc=vpc,
            access_log_bucket_name='foo',
            environments_parameters=environment_parameters,
            client_id='foo',
        )
    except Exception as e:
        assert e.args == (
            'OIDC configuration is not valid! If you aimed to configure OIDC listener please provide each of the params: authorization_endpoint, token_endpoint, issuer, client_id, client_secret, user_info_endpoint',
        )


def test_alb_uses_cdn_creates_a_cdn_sg(stack, vpc, environment_parameters):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=True,
        main_component_name='main_component_name',
        traffic_port=8888,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Cloudflare ' 'IPv4',
            'FromPort': 8888,
            'ToPort': 8888,
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000004',
        },
    )
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Cloudflare ' 'IPv6',
            'FromPort': 8888,
            'ToPort': 8888,
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000006',
        },
    )


def test_alb_creates_sg_not_cdn_and_not_public_allows_fao_private_access(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Prefix list FAO Clients',
            'FromPort': 8888,
            'ToPort': 8888,
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000001',
        },
    )


def test_alb_creates_sg_not_cdn_and_not_public_with_https_allows_fao_private_access_on_port_80(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        ssl_certificate_arn='ssl-cert-arn',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Prefix list FAO Clients',
            'FromPort': 8888,
            'ToPort': 8888,
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000001',
        },
    )
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Prefix list FAO Clients',
            'FromPort': 80,
            'ToPort': 80,
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000001',
        },
    )


def test_alb_creates_sg_not_cdn_and_not_public_with_upstream_allows_traffic_from_upstream(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        upstream_security_group='sg-00000001',
    )

    template = Template.from_stack(stack)
    sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupName': 'app_name_teststack_alb_sg'}},
    )

    sg_id = list(sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'From ' 'upstream',
            'FromPort': 8888,
            'GroupId': {'Fn::GetAtt': [sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': 'sg-00000001',
            'ToPort': 8888,
        },
    )


def test_alb_creates_sg_not_cdn_and_public_with_upstream_and_https_allows_upstream_traffic_on_port_80(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=True,
        upstream_security_group='sg-00000001',
        ssl_certificate_arn='ssl-cert-arn',
    )
    template = Template.from_stack(stack)
    sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupName': 'app_name_teststack_alb_sg'}},
    )
    sg_id = list(sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Upstream ' 'to ' 'HTTPS',
            'FromPort': 80,
            'GroupId': {'Fn::GetAtt': [sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': 'sg-00000001',
            'ToPort': 80,
        },
    )


def test_alb_creates_sg_not_cdn_and_public_with_upstream_and_https_allows_upstream_traffic_on_port_80_only_if_add_redirect_to_https_listener_is_enabled(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=True,
        upstream_security_group='sg-00000001',
        ssl_certificate_arn='ssl-cert-arn',
        add_redirect_to_https_listener=False,
    )
    template = Template.from_stack(stack)
    sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupName': 'app_name_teststack_alb_sg'}},
    )
    sg_id = list(sg.keys())[0]
    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Upstream ' 'to ' 'HTTPS',
            'FromPort': 80,
            'GroupId': {'Fn::GetAtt': [sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': 'sg-00000001',
            'ToPort': 80,
        },
        0,
    )


def test_alb_creates_sg_not_cdn_and_public_with_upstream_no_https_allows_upstream_traffic_to_traffic_port(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=True,
        upstream_security_group='sg-00000001',
    )
    template = Template.from_stack(stack)
    sg = template.find_resources(
        'AWS::EC2::SecurityGroup',
        {'Properties': {'GroupName': 'app_name_teststack_alb_sg'}},
    )
    sg_id = list(sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'From ' 'upstream',
            'FromPort': 8888,
            'GroupId': {'Fn::GetAtt': [sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourceSecurityGroupId': 'sg-00000001',
            'ToPort': 8888,
        },
    )


def test_alb_creates_sg_not_cdn_and_public_no_upstream_https_allows_traffic_from_everywhere_to_port_80(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=True,
        ssl_certificate_arn='ssl-cert-arn',
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'app_name_teststack_alb_sg',
            'SecurityGroupIngress': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Everyone to HTTP',
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'ToPort': 80,
                },
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Everyone to HTTPS',
                    'FromPort': 8888,
                    'IpProtocol': 'tcp',
                    'ToPort': 8888,
                },
            ],
        },
    )

    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'app_name_teststack_alb_sg',
            'SecurityGroupIngress': Match.array_with(
                [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Everyone to HTTP',
                        'FromPort': 80,
                        'IpProtocol': 'tcp',
                        'ToPort': 80,
                    }
                ]
            ),
        },
        1,
    )


def test_alb_creates_sg_not_cdn_and_public_no_upstream_https_allows_traffic_from_everywhere_to_port_80_only_if_add_redirect_to_https_listener_is_true(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=True,
        ssl_certificate_arn='ssl-cert-arn',
        add_redirect_to_https_listener=False,
    )
    template = Template.from_stack(stack)

    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'app_name_teststack_alb_sg',
            'SecurityGroupIngress': Match.array_with(
                [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Everyone to HTTP',
                        'FromPort': 80,
                        'IpProtocol': 'tcp',
                        'ToPort': 80,
                    }
                ]
            ),
        },
        0,
    )


def test_alb_creates_sg_not_cdn_and_public_no_upstream_https_allows_traffic_from_everywhere_to_port_443_only_when_allow_access_to_everyone_is_true(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=True,
        ssl_certificate_arn='ssl-cert-arn',
        allow_ingress_from_everyone=False,
    )
    template = Template.from_stack(stack)

    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'app_name_teststack_alb_sg',
            'SecurityGroupIngress': Match.array_with(
                [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Everyone to HTTPS',
                        'FromPort': 443,
                        'IpProtocol': 'tcp',
                        'ToPort': 443,
                    }
                ]
            ),
        },
        0,
    )

    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'app_name_teststack_alb_sg',
            'SecurityGroupIngress': Match.array_with(
                [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Everyone to HTTP',
                        'FromPort': 80,
                        'IpProtocol': 'tcp',
                        'ToPort': 80,
                    }
                ]
            ),
        },
        0,
    )


def test_alb_creates_sg_not_cdn_and_public_no_upstream_allows_traffic_from_everywhere_to_traffic_port(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Production',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=True,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'app_name_teststack_alb_sg',
            'SecurityGroupIngress': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Everyone',
                    'FromPort': 8888,
                    'IpProtocol': 'tcp',
                    'ToPort': 8888,
                }
            ],
        },
    )


def test_alb_creates_sg_fro_security_scan_tool_when_its_not_prod(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Development',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'app_name_teststack_alb_sg',
            'SecurityGroupIngress': [
                {
                    'CidrIp': '168.202.4.57/32',
                    'Description': 'From Security Scan tool',
                    'FromPort': 8888,
                    'IpProtocol': 'tcp',
                    'ToPort': 8888,
                }
            ],
        },
    )


def test_alb_enables_app_proxy_when_private(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Development',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Name': 'testalb', 'SecurityGroups': Match.array_with(['some-sg'])},
    )


def test_alb_adds_logging_to_bucket(stack, vpc, environment_parameters):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Development',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': Match.array_with(
                [
                    {'Key': 'access_logs.s3.enabled', 'Value': 'true'},
                    {'Key': 'access_logs.s3.bucket', 'Value': 'foo'},
                    {'Key': 'access_logs.s3.prefix', 'Value': 'app_name'},
                ]
            )
        },
    )


def test_alb_has_mandatory_tags(stack, vpc, environment_parameters):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'Tags': Match.array_with(
                [
                    {'Key': 'ApplicationName', 'Value': 'app_name'},
                    {'Key': 'Environment', 'Value': 'Development'},
                ]
            )
        },
    )


def test_alb_creates_dns_record_when_flagged(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        create_dns='True',
    )
    template = Template.from_stack(stack)
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testalb'}},
    )
    alb_id = list(alb.keys())[0]

    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {
            'Name': 'app_name.foo.bar.org.',
            'Type': 'A',
            'AliasTarget': {
                'DNSName': {
                    'Fn::Join': [
                        '',
                        ['dualstack.', {'Fn::GetAtt': [alb_id, 'DNSName']}],
                    ]
                },
                'HostedZoneId': {
                    'Fn::GetAtt': [alb_id, 'CanonicalHostedZoneID']
                },
            },
            'HostedZoneId': '00000000000000000000000000000000',
        },
    )


def test_alb_creates_target_group_with_default_values(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {
            'HealthCheckEnabled': True,
            'HealthCheckIntervalSeconds': 6,
            'HealthCheckPath': '/',
            'HealthCheckPort': '80',
            'HealthCheckProtocol': 'HTTP',
            'HealthCheckTimeoutSeconds': 5,
            'HealthyThresholdCount': 2,
            'Matcher': {'HttpCode': '200-399'},
            'Name': 'app-name-main-component-name-80',
            'Port': 80,
            'Protocol': 'HTTP',
            'UnhealthyThresholdCount': 2,
            'TargetGroupAttributes': [
                {'Key': 'stickiness.enabled', 'Value': 'false'}
            ],
        },
    )


def test_alb_creates_target_group_with_custom_values(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        healthy_threshold_count=10,
        unhealthy_threshold_count=20,
        ec2_health_check_path='/health',
        interval_in_seconds=40,
        timeout_in_seconds=30,
        stickiness_cookie_duration_in_hours=1,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {
            'HealthCheckEnabled': True,
            'HealthCheckIntervalSeconds': 40,
            'HealthCheckPath': '/health',
            'HealthCheckPort': '80',
            'HealthCheckProtocol': 'HTTP',
            'HealthCheckTimeoutSeconds': 30,
            'HealthyThresholdCount': 10,
            'Matcher': {'HttpCode': '200-399'},
            'Name': 'app-name-main-component-name-80',
            'Port': 80,
            'Protocol': 'HTTP',
            'UnhealthyThresholdCount': 20,
            'TargetGroupAttributes': [
                {'Key': 'stickiness.enabled', 'Value': 'true'},
                {'Key': 'stickiness.type', 'Value': 'lb_cookie'},
                {
                    'Key': 'stickiness.lb_cookie.duration_seconds',
                    'Value': '3600',
                },
            ],
        },
    )


def test_alb_creates_listener_without_https(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
    )

    template = Template.from_stack(stack)
    tg = template.find_resources(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {'Properties': {'Name': 'app-name-main-component-name-80'}},
    )
    tg_id = list(tg.keys())[0]
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testalb'}},
    )
    alb_id = list(alb.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {'TargetGroupArn': {'Ref': tg_id}, 'Type': 'forward'}
            ],
            'LoadBalancerArn': {'Ref': alb_id},
            'Port': 8888,
            'Protocol': 'HTTP',
        },
    )


def test_alb_creates_redirect_listener_with_https(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        ssl_certificate_arn='ssl-cert-arn',
    )

    template = Template.from_stack(stack)
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testalb'}},
    )
    alb_id = list(alb.keys())[0]

    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {
                    'RedirectConfig': {
                        'Host': '#{host}',
                        'Path': '/#{path}',
                        'Port': '8888',
                        'Protocol': 'HTTPS',
                        'Query': '#{query}',
                        'StatusCode': 'HTTP_301',
                    },
                    'Type': 'redirect',
                }
            ],
            'LoadBalancerArn': {'Ref': alb_id},
            'Port': 80,
            'Protocol': 'HTTP',
        },
    )

    template.resource_properties_count_is(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'LoadBalancerArn': {'Ref': alb_id},
            'Port': 80,
            'Protocol': 'HTTP',
        },
        1,
    )

    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroupIngress', {'FromPort': 80}, 1
    )


def test_alb_does_not_create_redirect_listener_with_https_when_add_redirect_to_https_listener_is_false(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        ssl_certificate_arn='ssl-cert-arn',
        add_redirect_to_https_listener=False,
    )

    template = Template.from_stack(stack)
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testalb'}},
    )
    alb_id = list(alb.keys())[0]

    template.resource_properties_count_is(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'LoadBalancerArn': {'Ref': alb_id},
            'Port': 80,
            'Protocol': 'HTTP',
        },
        0,
    )

    template.resource_properties_count_is(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'LoadBalancerArn': {'Ref': alb_id},
            'Port': 80,
            'Protocol': 'HTTP',
        },
        0,
    )

    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroupIngress', {'FromPort': 8888}, 1
    )

    template.resource_properties_count_is(
        'AWS::EC2::SecurityGroupIngress', {'FromPort': 80}, 0
    )


def test_alb_redirect_listener_with_https_is_disabled(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        ssl_certificate_arn='ssl-cert-arn',
        add_redirect_to_https_listener=False,
    )

    template = Template.from_stack(stack)
    template.resource_count_is('AWS::ElasticLoadBalancingV2::Listener', 1)


def test_alb_default_landing_https_listener_page(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        ssl_certificate_arn='ssl-cert-arn',
        will_create_tg=False,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {
                    'FixedResponseConfig': {
                        'MessageBody': 'app default landing page'
                    }
                }
            ]
        },
    )


def test_alb_default_landing_http_listener_page(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        will_create_tg=False,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {
                    'FixedResponseConfig': {
                        'MessageBody': 'app default landing page'
                    }
                }
            ]
        },
    )


def test_alb_creates_https_listener(stack, vpc, environment_parameters):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        ssl_certificate_arn='ssl-cert-arn',
    )

    template = Template.from_stack(stack)
    tg = template.find_resources(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {'Properties': {'Name': 'app-name-main-component-name-80'}},
    )
    tg_id = list(tg.keys())[0]
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testalb'}},
    )
    alb_id = list(alb.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {'TargetGroupArn': {'Ref': tg_id}, 'Type': 'forward'}
            ],
            'LoadBalancerArn': {'Ref': alb_id},
            'Port': 8888,
            'Protocol': 'HTTPS',
            'Certificates': [{'CertificateArn': 'ssl-cert-arn'}],
            'SslPolicy': 'ELBSecurityPolicy-FS-1-2-Res-2019-08',
        },
    )


def test_alb_creates_https_listener_with_oicd_config(
    stack, vpc, environment_parameters
):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main-component-name',
        traffic_port=8888,
        internet_facing=False,
        ssl_certificate_arn='ssl-cert-arn',
        authorization_endpoint='auth-endpoint',
        client_id='client-id',
        client_secret='client-secret',
        issuer='issuer',
        token_endpoint='token-endpoint',
        user_info_endpoint='user-info-endpoint',
    )

    template = Template.from_stack(stack)
    tg = template.find_resources(
        'AWS::ElasticLoadBalancingV2::TargetGroup',
        {'Properties': {'Name': 'app-name-main-component-name-80'}},
    )
    tg_id = list(tg.keys())[0]
    alb = template.find_resources(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {'Properties': {'Name': 'testalb'}},
    )
    alb_id = list(alb.keys())[0]
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::Listener',
        {
            'DefaultActions': [
                {
                    'AuthenticateOidcConfig': {
                        'AuthorizationEndpoint': 'auth-endpoint',
                        'ClientId': 'client-id',
                        'ClientSecret': 'client-secret',
                        'Issuer': 'issuer',
                        'TokenEndpoint': 'token-endpoint',
                        'UserInfoEndpoint': 'user-info-endpoint',
                    },
                    'Order': 1,
                    'Type': 'authenticate-oidc',
                },
                {
                    'Order': 2,
                    'TargetGroupArn': {
                        'Ref': tg_id,
                    },
                    'Type': 'forward',
                },
            ],
            'LoadBalancerArn': {
                'Ref': alb_id,
            },
            'Certificates': [{'CertificateArn': 'ssl-cert-arn'}],
            'Port': 8888,
            'Protocol': 'HTTPS',
            'SslPolicy': 'ELBSecurityPolicy-FS-1-2-Res-2019-08',
        },
    )


def test_alb_includes_cloudfront(app, stack, environment_parameters, vpc):
    cdn_domain = 'test.dev.fao.org'
    cdn_ssl_certificate_arn = 'arn:aws:acm:us-east-1:test:certificate/test'

    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Staging',
        vpc=vpc,
        access_log_bucket_name='foo',
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main-component-name',
        traffic_port=8888,
        will_implement_cdn='True',
        cdn_domain_names=[cdn_domain],
        cdn_ssl_certificate_arn=cdn_ssl_certificate_arn,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::CloudFront::Distribution',
        {
            'DistributionConfig': {
                'Aliases': [cdn_domain],
                'PriceClass': 'PriceClass_100',
                'ViewerCertificate': {
                    'AcmCertificateArn': cdn_ssl_certificate_arn,
                    'MinimumProtocolVersion': 'TLSv1.2_2021',
                    'SslSupportMethod': 'sni-only',
                },
            },
        },
    )


def test_alb_drop_invalid_header_fields(stack, vpc, environment_parameters):
    Alb(
        stack,
        'testalb',
        app_name='app_name',
        environment='Development',
        vpc=vpc,
        environments_parameters=environment_parameters,
        use_cdn=False,
        main_component_name='main_component_name',
        traffic_port=8888,
        internet_facing=False,
        will_drop_invalid_header_fields=True,
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::ElasticLoadBalancingV2::LoadBalancer',
        {
            'LoadBalancerAttributes': Match.array_with(
                [
                    {
                        'Key': 'routing.http.drop_invalid_header_fields.enabled',
                        'Value': 'true',
                    },
                ]
            )
        },
    )
