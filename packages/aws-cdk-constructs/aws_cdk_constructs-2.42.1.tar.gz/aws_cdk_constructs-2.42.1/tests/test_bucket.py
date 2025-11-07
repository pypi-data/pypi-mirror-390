import boto3
from aws_cdk.assertions import Template, Match
from moto import mock_s3

from aws_cdk_constructs import Bucket
from aws_cdk_constructs.bucket.bucket import check_if_bucket_exist


def test_check_bucket_exist_returns_false_when_no_bucket_name():
    assert check_if_bucket_exist(None) is False


def test_check_bucket_exist_returns_false_when_bucket_name_is_empty():
    assert check_if_bucket_exist('') is False


@mock_s3
def test_check_bucket_exist_returns_true_when_bucket_does_exist(mocker):
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket='mybucket')

    assert check_if_bucket_exist('mybucket') is True


@mock_s3
def test_check_if_bucket_exist_returns_false_when_bucket_does_not_exist(
    mocker,
):
    assert check_if_bucket_exist('mybucket') is False


def test_create_bucket_mandatory_tags(app, stack, environment_parameters):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
    )

    template = Template.from_stack(stack)
    from aws_cdk_constructs.utils import get_version

    version = get_version()
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'Tags': Match.array_with(
                [
                    {'Key': 'ApplicationName', 'Value': 'test-app'},
                    {'Key': 'Environment', 'Value': 'Development'},
                    {'Key': 'fao-cdk', 'Value': 'true'},
                    {'Key': 'fao-cdk-construct', 'Value': 'bucket'},
                    {'Key': 'fao-cdk-version', 'Value': version},
                ]
            )
        },
    )


def test_create_bucket_without_deletion_policy_on_dev(
    app, stack, environment_parameters
):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
    )

    template = Template.from_stack(stack)
    template.has_resource(
        'AWS::S3::Bucket',
        {'DeletionPolicy': 'Delete', 'UpdateReplacePolicy': 'Delete'},
    )


def test_create_bucket_with_deletion_policy_on_prod_and_public_read_access(
    app, stack, environment_parameters
):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Production',
        environments_parameters=environment_parameters,
        bucket_is_public='true',
        bucket_name='test-bucket-name',
    )

    template = Template.from_stack(stack)
    template.has_resource(
        'AWS::S3::Bucket',
        {'DeletionPolicy': 'Retain', 'UpdateReplacePolicy': 'Retain'},
    )


def test_create_bucket_with_default_options(
    app, stack, environment_parameters
):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {'BucketName': 'test-bucket-name'},
    )


def test_get_s3_bucket(app, stack, environment_parameters):
    bucket = Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
    )

    s3_bucket = bucket.bucket
    import aws_cdk

    assert isinstance(s3_bucket, aws_cdk.aws_s3.Bucket)


def test_bucket_with_website_documents(app, stack, environment_parameters):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name.foo.bar.org',
        bucket_website_index_document='index.html',
        bucket_website_error_document='error.html',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'WebsiteConfiguration': {
                'IndexDocument': 'index.html',
                'ErrorDocument': 'error.html',
            }
        },
    )

    template.has_resource_properties(
        'AWS::Route53::RecordSet',
        {
            'Name': 'test-bucket-name.foo.bar.org.',
            'Type': 'A',
            'AliasTarget': {
                'DNSName': 's3-website-eu-west-1.amazonaws.com',
                # AWS global namespace
                # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/quickref-s3.html
                'HostedZoneId': 'Z1BKCTXD74EZPE',
            },
            'HostedZoneId': '00000000000000000000000000000000',
        },
    )


def test_bucket_with_logic_id(app, stack, environment_parameters):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
        bucket_logic_id='logic-hid',
    )
    template = Template.from_stack(stack)
    bucket = template.find_resources('AWS::S3::Bucket')
    bucket_id = list(bucket.keys())[0]
    assert bucket_id.startswith('testbucketidlogichid')


def test_bucket_without_logic_id(app, stack, environment_parameters):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
    )
    template = Template.from_stack(stack)
    bucket = template.find_resources('AWS::S3::Bucket')
    bucket_id = list(bucket.keys())[0]
    assert bucket_id.startswith('testbucketidS3')


def test_bucket_cors_configuration(app, stack, environment_parameters, mocker):

    # Defined the function to mock
    mock_from_lookup = mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup')

    # Set up the mock to return a MagicMock object that simulates a VPC
    mock_vpc = mocker.MagicMock()
    vpc_cidr_block = '10.0.0.0/16'
    mock_vpc.vpc_cidr_block = vpc_cidr_block
    mock_from_lookup.return_value = mock_vpc

    Bucket(
        scope=stack,
        id='test-bucket-id-1',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name-public',
        bucket_is_public='true',
    )
    Bucket(
        scope=stack,
        id='test-bucket-id-2',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name-cdn',
        bucket_has_cdn='true',
    )
    Bucket(
        scope=stack,
        id='test-bucket-id-3',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name-public-cdn',
        bucket_has_cdn='true',
        bucket_is_public='true',
    )
    template = Template.from_stack(stack)

    # You don't want to add twice the CORS configuration
    # So we test that whatever combination of bucket_has_cdn and bucket_is_public a user provide
    # the CORS configuration is added only once
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'BucketName': 'test-bucket-name-public',
            'CorsConfiguration': {
                'CorsRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': [
                            'GET',
                            'POST',
                            'PUT',
                            'DELETE',
                            'HEAD',
                        ],
                        'AllowedOrigins': ['*'],
                    }
                ]
            },
        },
    )
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'BucketName': 'test-bucket-name-cdn',
            'CorsConfiguration': {
                'CorsRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': [
                            'GET',
                            'POST',
                            'PUT',
                            'DELETE',
                            'HEAD',
                        ],
                        'AllowedOrigins': ['*'],
                    }
                ]
            },
        },
    )
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'BucketName': 'test-bucket-name-public-cdn',
            'CorsConfiguration': {
                'CorsRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': [
                            'GET',
                            'POST',
                            'PUT',
                            'DELETE',
                            'HEAD',
                        ],
                        'AllowedOrigins': ['*'],
                    }
                ]
            },
        },
    )


def test_bucket_public_has_access_control(app, stack, environment_parameters):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
        bucket_is_public='true',
    )
    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::S3::Bucket', Match.not_({'AccessControl': 'Private'})
    )
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'CorsConfiguration': {
                'CorsRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': [
                            'GET',
                            'POST',
                            'PUT',
                            'DELETE',
                            'HEAD',
                        ],
                        'AllowedOrigins': ['*'],
                    }
                ]
            }
        },
    )
    bucket = template.find_resources('AWS::S3::Bucket')
    bucket_id = list(bucket.keys())[0]
    template.has_resource_properties(
        'AWS::S3::BucketPolicy',
        {
            'Bucket': {'Ref': bucket_id},
            'PolicyDocument': {
                'Statement': [
                    {
                        'Action': 's3:GetObject',
                        'Effect': 'Allow',
                        'Principal': {'AWS': '*'},
                        'Resource': {
                            'Fn::Join': [
                                '',
                                [
                                    {
                                        'Fn::GetAtt': [
                                            'testbucketidS31DAE7F65',
                                            'Arn',
                                        ]
                                    },
                                    '/*',
                                ],
                            ]
                        },
                    }
                ],
                'Version': '2012-10-17',
            },
        },
    )


def test_bucket_public_has_access_control(
    app, stack, environment_parameters, mocker
):

    # Defined the function to mock
    mock_from_lookup = mocker.patch('aws_cdk.aws_ec2.Vpc.from_lookup')

    # Set up the mock to return a MagicMock object that simulates a VPC
    mock_vpc = mocker.MagicMock()
    vpc_cidr_block = '10.0.0.0/16'
    mock_vpc.vpc_cidr_block = vpc_cidr_block
    mock_from_lookup.return_value = mock_vpc

    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
        bucket_has_cdn='true',
    )
    template = Template.from_stack(stack)
    iam_role = template.find_resources('AWS::IAM::Role')
    iam_role_id = list(iam_role.keys())[0]

    cloudflare_ips = [
        '173.245.48.0/20',
        '103.21.244.0/22',
        '103.22.200.0/22',
        '103.31.4.0/22',
        '141.101.64.0/18',
        '108.162.192.0/18',
        '190.93.240.0/20',
        '188.114.96.0/20',
        '197.234.240.0/22',
        '198.41.128.0/17',
        '162.158.0.0/15',
        '104.16.0.0/13',
        '104.24.0.0/14',
        '172.64.0.0/13',
        '131.0.72.0/22',
        '2400:cb00::/32',
        '2606:4700::/32',
        '2803:f800::/32',
        '2405:b500::/32',
        '2405:8100::/32',
        '2a06:98c0::/29',
        '2c0f:f248::/32',
    ]
    template.has_resource_properties(
        'AWS::S3::BucketPolicy',
        {
            'PolicyDocument': {
                'Statement': [
                    {
                        'Action': [
                            's3:PutBucketPolicy',
                            's3:GetBucket*',
                            's3:List*',
                            's3:DeleteObject*',
                        ],
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': {'Fn::GetAtt': [iam_role_id, 'Arn']}
                        },
                    },
                    {
                        'Action': 's3:GetObject',
                        'Condition': {
                            'NotIpAddress': {
                                'aws:SourceIp': cloudflare_ips,
                                'aws:VpcSourceIp': vpc_cidr_block,
                            },
                            'StringNotEquals': {'aws:SourceVpc': 'vpcid'},
                        },
                        'Effect': 'Deny',
                        'Principal': {'AWS': '*'},
                        'Resource': 'arn:aws:s3:::test-bucket-name/*',
                    },
                ],
                'Version': '2012-10-17',
            }
        },
    )
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'CorsConfiguration': {
                'CorsRules': [
                    {
                        'AllowedHeaders': ['*'],
                        'AllowedMethods': [
                            'GET',
                            'POST',
                            'PUT',
                            'DELETE',
                            'HEAD',
                        ],
                        'AllowedOrigins': ['*'],
                    }
                ]
            }
        },
    )


def test_bucket_is_versioned(app, stack, environment_parameters):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
        versioned=True,
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::S3::Bucket', {'VersioningConfiguration': {'Status': 'Enabled'}}
    )


def test_bucket_is_encrypted(app, stack, environment_parameters):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
        bucket_is_encrypted='true',
    )

    template = Template.from_stack(stack)
    key = template.find_resources('AWS::KMS::Key')
    key_id = list(key.keys())[0]

    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'BucketEncryption': {
                'ServerSideEncryptionConfiguration': [
                    {
                        'ServerSideEncryptionByDefault': {
                            'KMSMasterKeyID': {'Fn::GetAtt': [key_id, 'Arn']},
                            'SSEAlgorithm': 'aws:kms',
                        }
                    }
                ]
            }
        },
    )
    template.has_resource_properties(
        'AWS::KMS::Key',
        {
            'KeyPolicy': {
                'Statement': [
                    {
                        'Action': 'kms:*',
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': {
                                'Fn::Join': [
                                    '',
                                    [
                                        'arn:',
                                        {'Ref': 'AWS::Partition'},
                                        ':iam::00000000001:root',
                                    ],
                                ]
                            }
                        },
                        'Resource': '*',
                    }
                ],
                'Version': '2012-10-17',
            }
        },
    )


def test_bucket_is_encrypted_principals_arns(
    app, stack, environment_parameters
):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
        bucket_is_encrypted='true',
        encryption_allowed_principals_arns='testarn',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::KMS::Key',
        {
            'KeyPolicy': {
                'Statement': [
                    {
                        'Action': 'kms:*',
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': {
                                'Fn::Join': [
                                    '',
                                    [
                                        'arn:',
                                        {'Ref': 'AWS::Partition'},
                                        ':iam::00000000001:root',
                                    ],
                                ]
                            }
                        },
                        'Resource': '*',
                    },
                    {
                        'Action': [
                            'kms:Create*',
                            'kms:Describe*',
                            'kms:Decrypt',
                            'kms:Enable*',
                            'kms:List*',
                            'kms:Put*',
                            'kms:Update*',
                            'kms:Revoke*',
                            'kms:Disable*',
                            'kms:Get*',
                            'kms:Delete*',
                            'kms:ScheduleKeyDeletion',
                            'kms:CancelKeyDeletion',
                            'kms:GenerateDataKey',
                            'kms:TagResource',
                            'kms:UntagResource',
                        ],
                        'Effect': 'Allow',
                        'Principal': {'AWS': 'testarn'},
                        'Resource': '*',
                    },
                ],
                'Version': '2012-10-17',
            }
        },
    )


def test_bucket_is_privately_accessed_from_vpc(
    app, stack, environment_parameters
):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
        bucket_is_privately_accessed_from_vpc_over_http=True,
    )

    template = Template.from_stack(stack)

    bucket = template.find_resources('AWS::S3::Bucket')
    bucket_id = list(bucket.keys())[0]

    iam_role = template.find_resources('AWS::IAM::Role')
    iam_role_id = list(iam_role.keys())[0]

    template.has_resource_properties(
        'AWS::S3::BucketPolicy',
        {
            'PolicyDocument': {
                'Statement': [
                    {
                        'Action': [
                            's3:PutBucketPolicy',
                            's3:GetBucket*',
                            's3:List*',
                            's3:DeleteObject*',
                        ],
                        'Effect': 'Allow',
                        'Principal': {
                            'AWS': {'Fn::GetAtt': [iam_role_id, 'Arn']}
                        },
                        'Resource': [
                            {'Fn::GetAtt': [bucket_id, 'Arn']},
                            {
                                'Fn::Join': [
                                    '',
                                    [{'Fn::GetAtt': [bucket_id, 'Arn']}, '/*'],
                                ]
                            },
                        ],
                    },
                    {
                        'Action': 's3:GetObject',
                        'Effect': 'Allow',
                        'Principal': {'AWS': '*'},
                        'Resource': [
                            'arn:aws:s3:::test-bucket-name',
                            'arn:aws:s3:::test-bucket-name/*',
                        ],
                    },
                ],
                'Version': '2012-10-17',
            }
        },
    )


def test_bucket_includes_cloudfront(app, stack, environment_parameters):
    cdn_domain = 'test.dev.fao.org'
    cdn_ssl_certificate_arn = 'arn:aws:acm:us-east-1:test:certificate/test'
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
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


def test_bucket_with_object_ownership_when_no_public_read_access(
    app, stack, environment_parameters
):
    Bucket(
        scope=stack,
        id='test-bucket-id',
        app_name='test-app',
        environment='Development',
        environments_parameters=environment_parameters,
        bucket_name='test-bucket-name',
    )

    template = Template.from_stack(stack)
    template.has_resource_properties(
        'AWS::S3::Bucket',
        {
            'OwnershipControls': {
                'Rules': [{'ObjectOwnership': 'BucketOwnerPreferred'}]
            }
        },
    )
