import aws_cdk as cdk
from aws_cdk.assertions import Template

from aws_cdk_constructs import SecurityGroup


def test_creates_security_group_with_expected_tags(
    stack, vpc, environment_parameters
):
    SecurityGroup(
        stack,
        id='testsg',
        app_name='testapp',
        vpc=vpc,
        environment='Production',
        environments_parameters=environment_parameters,
        security_group_name='somename',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'Tags': [
                {'Key': 'ApplicationName', 'Value': 'testapp'},
                {'Key': 'Environment', 'Value': 'Production'},
            ]
        },
    )


def test_creates_sg_with_default_parameters(
    stack, vpc, environment_parameters
):
    SecurityGroup(
        stack,
        id='testsg',
        app_name='testapp',
        vpc=vpc,
        environment='Production',
        environments_parameters=environment_parameters,
        security_group_name='somename',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'somename',
            'SecurityGroupEgress': [
                {
                    'CidrIp': '0.0.0.0/0',
                    'Description': 'Allow all outbound traffic by default',
                    'IpProtocol': '-1',
                }
            ],
        },
    )


def test_creates_sg_with_expected_egress_rules(
    stack, vpc, environment_parameters
):
    SecurityGroup(
        stack,
        id='testsg',
        app_name='testapp',
        vpc=vpc,
        environment='Production',
        environments_parameters=environment_parameters,
        security_group_name='somename',
        allow_all_outbound=False,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::EC2::SecurityGroup',
        {
            'GroupName': 'somename',
            'SecurityGroupEgress': [
                {
                    'CidrIp': '255.255.255.255/32',
                    'Description': 'Disallow all traffic',
                    'FromPort': 252,
                    'IpProtocol': 'icmp',
                    'ToPort': 86,
                }
            ],
        },
    )


def test_creates_sg_with_fao_private_access_enabled(
    stack, vpc, environment_parameters
):
    sg = SecurityGroup(
        stack,
        id='testsg',
        app_name='testapp',
        vpc=vpc,
        environment='Production',
        environments_parameters=environment_parameters,
        security_group_name='somename',
    )
    sg.enable_fao_private_access(port=cdk.aws_ec2.Port.tcp(1234))

    template = Template.from_stack(stack)
    sg = template.find_resources(
        'AWS::EC2::SecurityGroup', {'Properties': {'GroupName': 'somename'}}
    )
    sg_id = list(sg.keys())[0]
    template.has_resource_properties(
        'AWS::EC2::SecurityGroupIngress',
        {
            'Description': 'Prefix list FAO Clients',
            'FromPort': 1234,
            'GroupId': {'Fn::GetAtt': [sg_id, 'GroupId']},
            'IpProtocol': 'tcp',
            'SourcePrefixListId': 'pl-00000000000000001',
            'ToPort': 1234,
        },
    )
