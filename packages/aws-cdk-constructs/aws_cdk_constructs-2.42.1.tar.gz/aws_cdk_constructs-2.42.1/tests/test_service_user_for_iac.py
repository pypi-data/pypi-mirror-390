import aws_cdk
import pytest
from aws_cdk.assertions import Template, Match

from aws_cdk_constructs import ServiceUserForIAC


@pytest.fixture
def svc_user_params(stack, environment_parameters):
    return {
        'scope': stack,
        'id': 'ServiceUserForIAC',
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


@pytest.fixture
def svc_role_params_multiple_repos(svc_role_params):
    return {
        **svc_role_params,
        'repo_name': 'githubreponame|githubreponame2',
    }


def test_service_usaer_get_service_user(stack, svc_user_params):
    svc_user = ServiceUserForIAC(**svc_user_params)
    service_user = svc_user.service_user
    assert (
        service_user.to_string() == 'teststack/ServiceUserForIAC/service_user'
    )
    assert isinstance(service_user, aws_cdk.aws_iam.User)


@pytest.mark.parametrize(
    'action, resources',
    [
        ('cloudformation:*', 'arn:aws:cloudformation:*:*:stack/app*'),
        ('ec2:*', 'arn:aws:ec2:eu-west-1:*:*/app*'),
        (
            ['elasticloadbalancingv2:*', 'elasticloadbalancing:*'],
            'arn:aws:elasticloadbalancing:eu-west-1:*:*/app*',
        ),
        (
            'rds:*',
            [
                'arn:aws:rds:eu-west-1:*:*:app*',
                'arn:aws:rds:eu-west-1:*:*:*default*',
            ],
        ),
        ('secretsmanager:*', 'arn:aws:secretsmanager:eu-west-1:*:*:app*'),
        ('lambda:*', 'arn:aws:lambda:*:*:*:app*'),
        ('autoscaling:*', 'arn:aws:autoscaling:eu-west-1:*:*:*:*app*'),
        (
            'elasticfilesystem:*',
            'arn:aws:elasticfilesystem:eu-west-1:*:*:*:*app*',
        ),
        (
            'iam:*',
            [
                'arn:aws:iam::*:user/app*',
                'arn:aws:iam::*:role/app*',
                'arn:aws:iam::*:group/app*',
                'arn:aws:iam::*:instance-profile/app*',
                'arn:aws:iam::*:policy/app*',
            ],
        ),
        (
            'cloudfront:*',
            [
                'arn:aws:cloudfront:eu-west-1:*:*:*:*app*',
                'arn:aws:cloudfront::*:distribution/*',
            ],
        ),
        ('kendra:*', 'arn:aws:kendra:eu-west-1:*:*app*'),
        ('cloudwatch:*', 'arn:aws:cloudwatch:*:*:dashboard/app*'),
        ('cloudwatch:*', 'arn:aws:cloudwatch:*:alarm:app*'),
    ],
)
def test_managed_policy_1_has_resource_filtered_policy(
    stack, svc_user_params, action, resources
):
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': action,
                            'Effect': 'Allow',
                            'Resource': resources,
                        }
                    ]
                )
            }
        },
    )


def test_managed_policy_1_has_all_resources_actions(stack, svc_user_params):
    actions = [
        'backup:CreateBackupPlan',
        'backup:CreateBackupSelection',
        'backup:DescribeBackupVault',
        'backup:CreateBackupVault',
        'cloudformation:Describe*',
        'cloudformation:ValidateTemplate',
        'cloudformation:ExecuteChangeSet',
        'cloudformation:*ChangeSet*',
        'cloudformation:GetTemplate',
        'cloudformation:ListStackResources',
        'ec2:CreateSecurityGroup',
        'ec2:*SecurityGroup*',
        'ec2:Describe*',
        'ec2:*Tag*',
        'serverlessrepo:SearchApplications',
        'serverlessrepo:GetApplication',
        'serverlessrepo:*CloudFormationTemplate',
        'serverlessrepo:*CloudFormationChangeSet',
        'serverlessrepo:List*',
        'serverlessrepo:Get*',
        'secretsmanager:GetRandomPassword',
        'elasticloadbalancingv2:Describe*',
        'elasticloadbalancing:Describe*',
        'elasticloadbalancing:Delete*',
        'elasticloadbalancingv2:*',
        'elasticloadbalancing:*',
        'elasticloadbalancing:ModifyLoadBalancerAttributes*',
        'autoscaling:Describe*',
        'iam:PutRolePolicy',
        'iam:getRolePolicy',
        'iam:GetUser',
        'iam:DeleteRolePolicy',
        'iam:DetachUserPolicy',
        'iam:ListAccessKeys',
        'iam:DeleteUser',
        'iam:AttachUserPolicy',
        'iam:PassRole',
        'iam:DeleteAccessKey',
        'rds:Describe*',
        'elasticfilesystem:*MountTarget*',
        'elasticfilesystem:DescribeMountTargets',
        'elasticfilesystem:DescribeFileSystems',
        'ec2:*Volume*',
        'elasticfilesystem:ListTagsForResource',
        'elasticfilesystem:DescribeFileSystemPolicy',
        'elasticfilesystem:TagResource',
        'elasticfilesystem:UntagResource',
        'autoscaling:DeletePolicy',
        'cognito-idp:*UserPoolClient',
        'cloudfront:TagResource',
        'ecs:Describe*',
        'ecs:List*',
        'ecs:Create*',
        'ecs:DiscoverPollEndpoint',
        'ecs:TagResource',
        'iam:ListAttachedRolePolicies',
        'iam:ListInstanceProfiles',
        'iam:ListRoles',
    ]
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [{'Action': actions, 'Effect': 'Allow', 'Resource': '*'}]
                )
            }
        },
    )


def test_managed_policy_1_has_default_buckets(stack, svc_user_params):
    buckets = [
        'arn:aws:s3:::app*',
        'arn:aws:s3:::awsserverlessrepo-changesets-*',
        'arn:aws:s3:::cdktoolkit*',
        'arn:aws:s3:::cdk-*',
    ]
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': 's3:*',
                            'Effect': 'Allow',
                            'Resource': buckets,
                        }
                    ]
                )
            }
        },
    )


def test_managed_policy_1_has_default_buckets_with_app_names_fixed(
    stack, svc_user_params
):
    buckets = [
        'arn:aws:s3:::app-name*',
        'arn:aws:s3:::appname*',
        'arn:aws:s3:::app.name*',
        'arn:aws:s3:::awsserverlessrepo-changesets-*',
        'arn:aws:s3:::cdktoolkit*',
        'arn:aws:s3:::cdk-*',
    ]
    svc_user_params['app_name'] = 'app-name'
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': 's3:*',
                            'Effect': 'Allow',
                            'Resource': buckets,
                        }
                    ]
                )
            }
        },
    )


def test_managed_policy_1_appends_code_bucket(stack, svc_user_params):
    buckets = [
        'arn:aws:s3:::app*',
        'arn:aws:s3:::awsserverlessrepo-changesets-*',
        'arn:aws:s3:::cdktoolkit*',
        'arn:aws:s3:::cdk-*',
        'arn:aws:s3:::code-bucket*',
    ]
    svc_user_params['s3_code_bucket_name'] = 'code-bucket'
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': 's3:*',
                            'Effect': 'Allow',
                            'Resource': buckets,
                        }
                    ]
                )
            }
        },
    )


def test_managed_policy_1_appends_code_bucket(stack, svc_user_params):
    buckets = [
        'arn:aws:s3:::app*',
        'arn:aws:s3:::awsserverlessrepo-changesets-*',
        'arn:aws:s3:::cdktoolkit*',
        'arn:aws:s3:::cdk-*',
        'arn:aws:s3:::assets-bucket*',
    ]
    svc_user_params['s3_assets_bucket_name'] = 'assets-bucket'
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': 's3:*',
                            'Effect': 'Allow',
                            'Resource': buckets,
                        }
                    ]
                )
            }
        },
    )


def test_managed_policy_1_has_ec2_with_conditions(stack, svc_user_params):
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': 'ec2:*',
                            'Effect': 'Allow',
                            'Resource': '*',
                            'Condition': {
                                'ForAnyValue:StringEquals': {
                                    'ec2:ResourceTag/ApplicationName': 'app'
                                }
                            },
                        }
                    ]
                )
            }
        },
    )


@pytest.mark.parametrize(
    'actions, resources, condition',
    [
        ('ecs:*', '*', 'ecs:ResourceTag/ApplicationName'),
        ('ecr:*', '*', 'ecr:ResourceTag/ApplicationName'),
    ],
)
def test_managed_policy_2_has_stringlike_policies(
    stack, svc_user_params, actions, resources, condition
):
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': actions,
                            'Condition': {'StringLike': {condition: 'app'}},
                            'Effect': 'Allow',
                            'Resource': resources,
                        }
                    ]
                )
            }
        },
    )


def test_managed_policy_2_has_ecs(stack, svc_user_params):
    ServiceUserForIAC(**svc_user_params)
    template = Template.from_stack(stack)

    template.has_resource_properties(
        'AWS::IAM::ManagedPolicy',
        {
            'PolicyDocument': {
                'Statement': Match.array_with(
                    [
                        {
                            'Action': [
                                'ssm:GetParameter',
                                'ssm:GetParameters',
                                'ssm:GetParametersByPath',
                            ],
                            'Effect': 'Allow',
                            'Resource': 'arn:aws:ssm:*:*:parameter/aws/service/ecs*',
                        }
                    ]
                )
            }
        },
    )


def test_srvrole_is_present_when_flag(stack, svc_role_params):
    ServiceUserForIAC(**svc_role_params)
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
            'ManagedPolicyArns': [
                {'Ref': 'ServiceUserForIACmanagedpolicyiacone579637DA'},
                {'Ref': 'ServiceUserForIACmanagedpolicyiactwo5DBE53FF'},
                {'Ref': 'ServiceUserForIACserviceuserpolicies158D25B5'},
                {'Ref': 'ServiceUserForIACserviceuserpolicycdk17A5FE9C'},
            ],
            'RoleName': 'SRVROLE-app_development_iac',
        },
    )


def test_srvrole_is_present_when_flag_multiple_repos(
    stack, svc_role_params_multiple_repos
):
    ServiceUserForIAC(**svc_role_params_multiple_repos)
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
                                    'repo:un-fao/githubreponame:*',
                                    'repo:un-fao/githubreponame2:*',
                                ],
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
            'ManagedPolicyArns': [
                {'Ref': 'ServiceUserForIACmanagedpolicyiacone579637DA'},
                {'Ref': 'ServiceUserForIACmanagedpolicyiactwo5DBE53FF'},
                {'Ref': 'ServiceUserForIACserviceuserpolicies158D25B5'},
                {'Ref': 'ServiceUserForIACserviceuserpolicycdk17A5FE9C'},
            ],
            'RoleName': 'SRVROLE-app_development_iac',
        },
    )


def test_srvusr_is_tagged_when_svcrrole_exists(stack, svc_role_params):
    ServiceUserForIAC(**svc_role_params)
    template = Template.from_stack(stack)

    some = template.to_json()
    template.has_resource_properties(
        'AWS::IAM::User',
        {'Tags': Match.array_with([{'Key': 'GHA_ROLE', 'Value': 'True'}])},
    )
