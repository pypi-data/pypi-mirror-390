import aws_cdk
import pytest
from aws_cdk.assertions import Template, Match

from aws_cdk_constructs import ServiceUserForStaticAssets


@pytest.fixture
def svc_user_params(stack, environment_parameters):
    return {
        'scope': stack,
        'id': 'ServiceUserForStaticAssets',
        'app_name': 'app',
        'environment': 'Development',
        'environments_parameters': environment_parameters,
    }


@pytest.fixture
def svc_role_params(stack, environment_parameters):
    return {
        'scope': stack,
        'id': 'ServiceUserForIAC',
        'app_name': 'app',
        'environment': 'Development',
        'environments_parameters': environment_parameters,
        'repo_name': 'githubreponame',
    }


def test_service_user_get_service_user(stack, svc_user_params):
    svc_user = ServiceUserForStaticAssets(**svc_user_params)
    service_user = svc_user.service_user
    assert (
        service_user.to_string()
        == 'teststack/ServiceUserForStaticAssets/service_user'
    )
    assert isinstance(service_user, aws_cdk.aws_iam.User)


def test_service_users_adds_s3_bucket(stack, svc_user_params):
    svc_user_params['s3_bucket_name'] = 'bucket-parameter'
    service_user = ServiceUserForStaticAssets(**svc_user_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': [
                    {
                        'Action': 's3:*',
                        'Effect': 'Allow',
                        'Resource': [
                            'arn:aws:s3:::bucket-parameter',
                            'arn:aws:s3:::bucket-parameter/*',
                        ],
                    }
                ]
            }
        },
    )


def test_srvrole_is_present_when_flag(stack, svc_role_params):
    ServiceUserForStaticAssets(**svc_role_params)
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::IAM::Role',
        {
            'AssumeRolePolicyDocument': {
                'Statement': [
                    {
                        'Action': 'sts:AssumeRoleWithWebIdentity',
                        'Condition': {
                            'StringEquals': {
                                'token.actions.githubusercontent.com:aud': 'sts.amazonaws.com'
                            },
                            'StringLike': {
                                'token.actions.githubusercontent.com:sub': [
                                    'repo:un-fao/githubreponame:*'
                                ]
                            },
                        },
                        'Effect': 'Allow',
                        'Principal': {
                            'Federated': 'arn:aws:iam::00000000000:oidc-provider/token.actions.githubusercontent.com'
                        },
                    }
                ],
                'Version': '2012-10-17',
            },
            'RoleName': 'SRVROLE-app_development_static_assets',
        },
    )


def test_srvusr_is_tagged_when_svcrrole_exists(stack, svc_role_params):
    ServiceUserForStaticAssets(**svc_role_params)
    template = Template.from_stack(stack)

    some = template.to_json()
    template.has_resource_properties(
        'AWS::IAM::User',
        {'Tags': Match.array_with([{'Key': 'GHA_ROLE', 'Value': 'True'}])},
    )
