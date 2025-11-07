import os

import aws_cdk as cdk
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_elasticloadbalancingv2 as _alb
from aws_cdk import aws_elasticloadbalancingv2_targets as _alb_targets
from aws_cdk import aws_iam as _iam
from aws_cdk import Stack
from constructs import Construct

from aws_cdk_constructs.load_balancer import Alb
from aws_cdk_constructs.utils import (
    get_version,
    normalize_environment_parameter,
)

dirname = os.path.dirname(__file__)


class WindowsServer(Construct):
    """

    The FAO CDK WindowsServer Construct creates infrastructures based on Windows AMIs

    The construct automatically enables the following main features:

    -	Creates an EC2 instances using the provided AMI ID;
    -	Native integration with the FAO Instance Scheduler to automatically control the uptime of the EC2 instances;
    -	Optional native integration with FAO CDK Load Balancer construct to make the EC2 instance publicly available;

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:
        scope (Construct): Parent construct

        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliance. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        main_component_name (str): This is just a metadata. Textually specify the component the EC2 instance will host (e.g. tomcat, drupal, ...)

        hostname (str): The hostname of the EC2 instance. This will be used to generate the 'Instance Name' tag for CSI compliance.

        private_ip_address (str): The private IP address of the EC2 instance.

        ssl_certificate_arn (str): In case you want to enable HTTPS for your stack, specify the SSL certificate ARN to use. This configuration will force the creation of 2 load balancer Listeners (str)one on port 443 that proxies to the Target Group, a second one on port 80 to redirect the traffic to port 443 and enforce HTTPS. In case the application implements HTTPS, specify the ARN of the SSL Certificate to use. You can find it in AWS Certificate Manager

        ec2_key_id (Optional | str): The ID of the EC2 key pair to use for the EC2 instance. If not provided, the default key name will be the hostname

        ec2_ami_id (str): The AMI ID of the Windows Server.

        ec2_instance_type (str): Specify the instance type of your EC2 instance. EC2 instance types https://aws.amazon.com/ec2/instance-types

        traffic_port (str): Specify the port the Application Load Balancer will listen to. This is the port the final users will contact to browse the system. If HTTPS is enabled, this parameter will be forced to be 443. This is the port that the application will use to accept traffic (e.g. if the application uses HTTPS, specify 443; if the application uses HTTP, specify 80; etc.).

        ec2_traffic_port (str): Specify the port the EC2 instance will listen to. This is used also as the Target Group Health check configuration port. For example (str)if you EC2 is equipped with an Apache Tomcat, listening on port 8080, use this parameter to specify 8080. It's important to note that this is not port the final user will use to connect to the system, as the Load Balancer will be in-front of the EC2.This is the port that the load balancer will use to forward traffic to the EC2 (e.g. Tomcat uses port 8080, Node.js uses port 3000).

        ec2_traffic_protocol (aws_alb.Protocol): Specify the protocol the EC2 instance will listen to. This is used also as the Target Group Health check configuration protocol. Default aws_alb.Protocol.HTTP

        access_log_bucket_name (str): Default: "fao-elb-logs". To enable Load Balancer access logs to be stored in the specified S3 bucket

        authorization_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        client_id (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        client_secret (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        issuer (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        token_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        user_info_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        will_be_public (str): Whether of not the application should be publicly accessible

        stickiness_cookie_duration_in_hours: (Optional | str) if provided sticky sessions will be configured for the Application Load Balancer.

        load_balancer_idle_timeout_in_seconds: (Optional | str) if provided idle timeout will be  configured for the Application Load Balancer.

        ec2_health_check_path (str):  Specify the Target Group health check path to use to monitor the state of the EC2 instances. EC2 instances will be constantly monitored, performing requests to this path. The request must receive a successful response code to consider the EC2 healthy. Otherwise the EC2 will be terminated and regenerated. It must start with a slash "/"

        will_use_cdn (str): Whether or not the Application Load Balancer should receive traffic only from Cloudflare CDN

        dns_record: (Optional | str) The DNS record associated to the Load Balancer. This is applied only in Development and QA environment. If multiple Load Balancers are included in the stack, the parameter is mandatory (Default is app_name)

        create_dns (Optional | str): to enable/disable dns creation - format Boolean (`true`, `false`). Default: true

        create_load_balancer (Optional | str): to enable/disable load balancer creation - format Boolean (`true`, `false`). Default: true

        upstream_security_group (str): In case the application is published as part of a parent app, please specify the security group of the resource will sent traffic to the app (e.g. if the app is part of fao.org website, given that the app will be receive traffic from the fao.org reverse proxies, specify the fao.org reverse proxy security group ID)

        tag_scheduler_uptime (str): specifies the time range in which the AWS resource should be kept up and running - format `HH:mm-HH:mm` (i.e. 'start'-'end'), where the 'start' time must be before 'end'

        tag_scheduler_uptime_days (str): weekdays in which the `SchedulerUptime` tag should be enforced. If not specified, `SchedulerUptime` will be enforced during each day of the week - format integer from 1 to 7, where 1 is Monday

        tag_scheduler_uptime_skip (str): to skip optimization check - format Boolean (`true`, `false`),

        ebs_volume_size (str): In case you want to create a secondary EBS volume for your EC2 instance, this parameter is used to specify the volume size. The parameter specify the desired GB. Only use this parameter when your system cannot horizontally scale!

        omit_cloudformation_template_outputs(bool): Omit the generation of CloudFormation template outputs. Default: false

        will_drop_invalid_headers (Optional | str): Indicates whether HTTP headers with invalid header fields are removed by the load balancer ('true') or routed to targets ('false'). Default: false
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name: str,
        environment: str,
        environments_parameters: dict,
        main_component_name: str,
        private_ip_address: str,
        ec2_ami_id: str,
        hostname: str,
        ec2_key_id: str = None,
        ssl_certificate_arn: str = None,
        ec2_instance_type: str = 't3.medium',
        ec2_traffic_port: int = '80',
        ec2_traffic_protocol: _alb.Protocol = _alb.Protocol.HTTP,
        traffic_port: int = '80',
        access_log_bucket_name: str = 'fao-elb-logs',
        authorization_endpoint: str = None,
        token_endpoint: str = None,
        will_be_public: bool = False,
        issuer: str = None,
        client_id: str = None,
        client_secret: str = None,
        user_info_endpoint: str = None,
        stickiness_cookie_duration_in_hours: str = None,
        load_balancer_idle_timeout_in_seconds: str = None,
        upstream_security_group: str = None,
        ec2_health_check_path: str = None,
        will_use_cdn: str = 'false',
        dns_record: str = None,
        create_dns: str = 'True',
        create_load_balancer: bool = True,
        tag_scheduler_uptime: str = '',
        tag_scheduler_uptime_days: str = '',
        tag_scheduler_uptime_skip: str = '',
        ebs_volume_size: str = '150',
        omit_cloudformation_template_outputs: bool = False,
        will_drop_invalid_headers: str = 'False',
        **kwargs,
    ):

        super().__init__(scope, id, **kwargs)

        # Apply mandatory tags
        cdk.Tags.of(self).add(
            'ApplicationName',
            app_name,
            apply_to_launched_instances=True,
        )
        cdk.Tags.of(self).add(
            'Environment',
            environment,
            apply_to_launched_instances=True,
        )

        # Apply FAO CDK tags
        cdk.Tags.of(self).add('fao-cdk-construct', 'windows-server')
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk-version', get_version())
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk', 'true')

        self.environment = normalize_environment_parameter(environment)
        self.app_name = app_name.lower().strip()
        self.aws_account = environments_parameters['accounts'][
            environment.lower()
        ]
        self.hostname = hostname
        self.id = id

        is_production = (
            self.environment == 'production'
            or self.environment == 'sharedservices'
        )
        is_not_production = not is_production

        self.ssl_certificate_arn = ssl_certificate_arn
        self.ec2_instance_type = ec2_instance_type
        self.ec2_traffic_port = ec2_traffic_port
        self.ec2_traffic_protocol = ec2_traffic_protocol
        self.traffic_port = traffic_port
        self.access_log_bucket_name = access_log_bucket_name
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.will_be_public = will_be_public
        self.issuer = issuer
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_info_endpoint = user_info_endpoint
        self.stickiness_cookie_duration_in_hours = (
            stickiness_cookie_duration_in_hours
        )
        self.load_balancer_idle_timeout_in_seconds = (
            load_balancer_idle_timeout_in_seconds
        )
        self.upstream_security_group = upstream_security_group
        self.ec2_health_check_path = ec2_health_check_path
        self.will_use_cdn = will_use_cdn
        self.dns_record = dns_record
        self.create_dns = create_dns
        self.create_load_balancer = create_load_balancer
        self.private_ip_address = private_ip_address
        self.ec2_key_id = ec2_key_id or self.hostname

        is_public = (
            will_be_public
            and isinstance(will_be_public, str)
            and will_be_public.lower() == 'true'
        )
        use_cdn = (
            will_use_cdn
            and isinstance(will_use_cdn, str)
            and will_use_cdn.lower() == 'true'
        )

        self.vpc = _ec2.Vpc.from_vpc_attributes(
            self,
            'VPC',
            vpc_id=self.aws_account['vpc'],
            public_subnet_ids=self.aws_account['public_subnet_ids'],
            private_subnet_ids=self.aws_account['private_subnet_ids'],
            availability_zones=self.aws_account['availability_zones'],
        )

        self.instance_type = _ec2.InstanceType(ec2_instance_type)
        self.ec2_ami_id = ec2_ami_id
        self.machine_image = _ec2.GenericWindowsImage(
            {'eu-west-1': self.ec2_ami_id}
        )

        # ==============================================================================
        # EC2 Instance Role
        # ==============================================================================
        self.ec2_role = _iam.Role(
            self,
            f'ec2_role_{app_name}_{main_component_name}',
            description=app_name + '_ec2_role',
            assumed_by=_iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                # AWS managed policy to allow sending logs and custom metrics to Cloudwatch
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    'CloudWatchAgentServerPolicy'
                ),
                # AWS managed policy to allow Session Manager console connections to the EC2 instance
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    'AmazonSSMManagedInstanceCore'
                ),
            ],
            role_name=app_name + '_ec2_role',
        )

        # IAM policies (inline)
        self.ec2_role.attach_inline_policy(
            _iam.Policy(
                self,
                'ec2_policies',
                statements=[
                    # Policy for EBS
                    _iam.PolicyStatement(
                        actions=[
                            'ec2:AttachVolume',
                            'ec2:DescribeVolumeStatus',
                        ],
                        resources=['*'],
                    ),
                    # S3 access to get from the config bucket configuration files, code packages and libraries
                    _iam.PolicyStatement(
                        actions=['s3:List*'],
                        resources=[
                            'arn:aws:s3:::'
                            + self.aws_account['s3_config_bucket'],
                            'arn:aws:s3:::'
                            + self.aws_account['s3_config_bucket']
                            + '/'
                            + app_name
                            + '/*',
                        ],
                    ),
                    _iam.PolicyStatement(
                        actions=['s3:*'],
                        resources=[
                            'arn:aws:s3:::'
                            + self.aws_account['s3_config_bucket']
                            + '/'
                            + app_name
                            + '/'
                            + environment,
                            'arn:aws:s3:::'
                            + self.aws_account['s3_config_bucket']
                            + '/'
                            + app_name
                            + '/'
                            + environment
                            + '/*',
                        ],
                    ),
                    # S3 access to get SentinelOne
                    _iam.PolicyStatement(
                        actions=['s3:List*', 's3:Get*'],
                        resources=[
                            'arn:aws:s3:::fao-aws-configuration-files'
                            + '/windows/*',
                        ],
                    ),
                    # KMS LimitedAccess just to use the keys
                    _iam.PolicyStatement(
                        actions=[
                            'kms:Decrypt',
                            'kms:Encrypt',
                            'kms:ReEncrypt*',
                            'kms:GenerateDataKey*',
                            'kms:Describe*',
                        ],
                        resources=[
                            'arn:aws:kms:eu-west-1:'
                            + Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ':key/'
                            + self.aws_account['kms_ssm_key'],
                            'arn:aws:kms:eu-west-1:'
                            + Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ':key/'
                            + self.aws_account['kms_ebs_key'],
                        ],
                    ),
                    _iam.PolicyStatement(
                        actions=[
                            'kms:CreateGrant',
                            'kms:ListGrants',
                            'kms:RevokeGrant',
                        ],
                        resources=[
                            'arn:aws:kms:eu-west-1:'
                            + Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ':key/'
                            + self.aws_account['kms_ebs_key'],
                        ],
                    ),
                    # SSM Parameter store access
                    _iam.PolicyStatement(
                        actions=[
                            'ssm:Describe*',
                            'ssm:Get*',
                            'ssm:List*',
                        ],
                        resources=[
                            'arn:aws:kms:eu-west-1:'
                            + Stack.of(
                                self
                            ).account  # Reference for 'AWS::AccountId'
                            + ':parameter/'
                            + app_name
                            + '/*'
                        ],
                    ),
                ],
            )
        )

        # ==============================================================================
        # EC2 Security group
        # ==============================================================================
        self.ec2_security_group = _ec2.SecurityGroup(
            self,
            f'ec2_sg_{app_name}_{main_component_name}',
            vpc=self.vpc,
            security_group_name=app_name + '_ec2_sg',
            allow_all_outbound=True,
        )

        # ==============================================================================
        # EC2 Instance
        # ==============================================================================
        self.instance = _ec2.Instance(
            self,
            f'ec2_instance_{app_name}_{main_component_name}',
            vpc=self.vpc,
            instance_type=self.instance_type,
            machine_image=self.machine_image,
            instance_name=self.hostname,
            block_devices=[
                _ec2.BlockDevice(
                    device_name='/dev/sda1',
                    volume=_ec2.BlockDeviceVolume.ebs(150),
                ),
                _ec2.BlockDevice(
                    device_name='xvdh',
                    volume=_ec2.BlockDeviceVolume.ebs(int(ebs_volume_size)),
                ),
            ],
            role=self.ec2_role,
            key_name=self.ec2_key_id,
            security_group=self.ec2_security_group,
            private_ip_address=self.private_ip_address,
        )

        user_data_file_path = os.path.join(dirname, 'user_data.ps1')

        # Read the base user data from file
        with open(user_data_file_path) as base_user_data_content:
            base_user_data = base_user_data_content.read()
        base_user_data_content.close()

        # Inject parameter within the user data script template.
        base_user_data = base_user_data.replace('_EC2Name_', self.hostname)
        base_user_data = base_user_data.replace(
            '_EC2SubnetId_', self.aws_account['private_subnet_ids'][0]
        )
        base_user_data = base_user_data.replace('_DNSType_', 'DNSHQ')

        self.instance.add_user_data(base_user_data)

        # Add Windows admin bastion host, IT Security scan, Active Directory access security groups
        fao_mandatory_security_groups = [
            {
                'id': self.aws_account[
                    'bastion_host_windows_admin_security_group'
                ],
                'name': 'bastion_windows_team',
            },
            {
                'id': self.aws_account['scan_target_security_group'],
                'name': 'it_sec_scan',
            },
            {
                'id': self.aws_account['domain_control_access_security_group'],
                'name': 'domain_control_access',
            },
        ]

        for sec_group in fao_mandatory_security_groups:
            self.instance.add_security_group(
                _ec2.SecurityGroup.from_security_group_id(
                    self,
                    sec_group['name'] + 'sg',
                    sec_group['id'],
                    mutable=False,
                )
            )

        # Apply
        if is_not_production:
            if tag_scheduler_uptime_skip:
                cdk.Tags.of(self.instance).add(
                    'SchedulerSkip', tag_scheduler_uptime_skip
                )

            if tag_scheduler_uptime:
                cdk.Tags.of(self.instance).add(
                    'SchedulerUptime', tag_scheduler_uptime
                )

            if tag_scheduler_uptime_days:
                cdk.Tags.of(self.instance).add(
                    'SchedulerUptimeDays', tag_scheduler_uptime_days
                )

        # ==============================================================================
        # Optional: create the load balancer
        # ==============================================================================
        if create_load_balancer:

            drop_invalid_headers = (
                will_drop_invalid_headers
                and isinstance(will_drop_invalid_headers, str)
                and will_drop_invalid_headers.lower() == 'true'
            )

            # Create the Application Load Balancer
            alb = Alb(
                scope=self,
                id='alb',
                app_name=app_name,
                environment=environment,
                environments_parameters=environments_parameters,
                internet_facing=is_public,
                load_balancer_name='-'.join(
                    [app_name, main_component_name, 'alb']
                ),
                use_cdn=use_cdn,
                main_component_name=main_component_name,
                load_balancer_idle_timeout_in_seconds=load_balancer_idle_timeout_in_seconds,
                dns_record=dns_record,
                access_log_bucket_name=access_log_bucket_name,
                vpc=self.vpc,
                create_dns=create_dns,
                traffic_port=traffic_port,
                ec2_traffic_port=ec2_traffic_port,
                ec2_health_check_path=ec2_health_check_path,
                ec2_traffic_protocol=ec2_traffic_protocol,
                stickiness_cookie_duration_in_hours=stickiness_cookie_duration_in_hours,
                ssl_certificate_arn=ssl_certificate_arn,
                authorization_endpoint=authorization_endpoint,
                token_endpoint=token_endpoint,
                issuer=issuer,
                client_id=client_id,
                client_secret=client_secret,
                user_info_endpoint=user_info_endpoint,
                upstream_security_group=upstream_security_group,
                will_drop_invalid_header_fields=drop_invalid_headers,
            )

            self.alb = alb.alb
            self.alb_construct = alb
            self._tg = alb.tg
            self.listener = alb.listener

            # add ingress to ec2 sg from alb sg
            self.ec2_security_group.add_ingress_rule(
                peer=alb.security_group,
                connection=_ec2.Port.tcp(int(ec2_traffic_port)),
                description='From Load Balancer',
            )

            # Register the EC2 as ALB target
            self.listener.add_targets(
                f'target{app_name}_{main_component_name}',
                port=int(ec2_traffic_port),
                protocol=_alb.ApplicationProtocol.HTTP,
                targets=[
                    _alb_targets.InstanceIdTarget(
                        instance_id=self.instance.instance_id,
                        port=int(ec2_traffic_port),
                    )
                ],
            )
