import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template, Match
from aws_cdk import aws_elasticloadbalancingv2 as _alb

from aws_cdk_constructs.windows_server.windows_server import WindowsServer


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
def windows_server(stack, vpc, mocker, environment_parameters):
    mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup', return_value=vpc)

    return WindowsServer(
        scope=stack,
        id='x',
        app_name='test-app',
        environment='development',
        environments_parameters=environment_parameters,
        main_component_name='input-system',
        private_ip_address='10.0.0.1',
        ec2_key_id='my-fake-key',
        ec2_ami_id='ami-04d48649b5e67e3be',
        hostname='AWSPRTEST',
        create_load_balancer=False,
    )


@pytest.fixture
def template(stack, windows_server):
    return Template.from_stack(stack)


def test_construct_default_values(stack, windows_server):

    assert windows_server.ssl_certificate_arn == None
    assert windows_server.ec2_instance_type == 't3.medium'
    assert windows_server.ec2_traffic_port == '80'
    assert windows_server.ec2_traffic_protocol == _alb.Protocol.HTTP
    assert windows_server.traffic_port == '80'
    assert windows_server.access_log_bucket_name == 'fao-elb-logs'
    assert windows_server.authorization_endpoint == None
    assert windows_server.token_endpoint == None
    assert windows_server.will_be_public == False
    assert windows_server.issuer == None
    assert windows_server.client_id == None
    assert windows_server.client_secret == None
    assert windows_server.user_info_endpoint == None
    assert windows_server.stickiness_cookie_duration_in_hours == None
    assert windows_server.load_balancer_idle_timeout_in_seconds == None
    assert windows_server.upstream_security_group == None
    assert windows_server.ec2_health_check_path == None
    assert windows_server.will_use_cdn == 'false'
    assert windows_server.dns_record == None
    assert windows_server.create_dns == 'True'
    assert isinstance(
        windows_server.ec2_security_group, cdk.aws_ec2.SecurityGroup
    )


def test_template_has_ec2_instance(template):
    template.resource_count_is('AWS::EC2::Instance', 1)


def test_ec2_ami(windows_server):
    assert windows_server.ec2_ami_id == 'ami-04d48649b5e67e3be'


def test_ec2_private_id(windows_server):
    assert windows_server.private_ip_address == '10.0.0.1'
