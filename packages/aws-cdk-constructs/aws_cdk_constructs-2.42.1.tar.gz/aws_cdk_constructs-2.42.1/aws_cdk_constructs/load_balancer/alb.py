from aws_cdk import (
    aws_elasticloadbalancingv2 as _alb,
    aws_ec2 as _ec2,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_ssm as _ssm,
    aws_s3 as _s3,
    Tags,
    Duration,
    SecretValue,
    aws_certificatemanager as _certificate,
    aws_cloudfront as _cloudfront,
    aws_cloudfront_origins as _cloudfront_origins,
)
from constructs import Construct
from typing import Union

from aws_cdk_constructs.security_group import SecurityGroup

from botocore.exceptions import ClientError
from ..utils import normalize_environment_parameter


class Alb(Construct):
    """
    The FAO CDK Alb Construct creates AWS Application Load Balancer resources.

    The construct automatically enables the following main features:

    -	Creates private and internet-facing AWS Application Load Balancers with custom configurations;
    -	AWS Application Load Balancer integration with AWS Cognito to only allow authenticated requests;
    -	HTTP and HTTPS listeners setup;
    -	SSL configuration using FAO or custom certificates;
    -	Sticky session setup;
    -	Azure AppProxy, FAO HQ & private clients, Pulse secure VPN integration for private Load Balancers;
    -	Load Balancer logs collection;
    -	AWS Target Group creation and health-check configuration;
    -	Private DNS record creation for non-Production environments;
    -	Enable access only from Cloudflare v4 and v6 IP ranges;

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org


    Args:
        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        vpc (_ec2.IVpc): The VPC in which the load balancer will be created

        access_log_bucket_name (str): Default: "fao-elb-logs". To enable Load Balancer access logs to be stored in the specified S3 bucket

        security_group (Optional | [aws_ec2.SecurityGroup]): The security group to associate with the load balancer. If CDN is enabled, this security group is ignored

        upstream_security_group (str): In case the application is published as part of a parent app, please specify the security group of the resource will sent traffic to the app (e.g. if the app is part of fao.org website, given that the app will be receiving traffic from the fao.org reverse proxies, specify the fao.org reverse proxy security group ID)

        internet_facing (str): if the load balancer should be internet-facing or not

        load_balancer_name (str): the load balancer name

        use_cdn (bool): if the Application Load Balancer should accept traffic only from CDN. If this is set to True, the `
        _group` parameter will be ignored

        main_component_name (Optional | str): This is just a metadata. Textually specify the component the EC2 instance will host (e.g. tomcat, drupal, ...)

        load_balancer_idle_timeout_in_seconds: (Optional | str) if provided idle timeout will be  configured for the Application Load Balancer. (Default is 50s)

        dns_record: (Optional | str) The DNS record associated to the Load Balancer. This is applied only in Development and QA environment. If multiple Load Balancers are included in the stack, the parameter is mandatory (Default is app_name)

        create_dns: (Optional | str) to enable/disable dns creation - format Boolean (`true`, `false`). Default: true

        traffic_port (str): Specify the port the Application Load Balancer will listen to. This is the port the final users will contact to browse the system. If HTTPS is enabled, this parameter will be forced to be 443. This is the port that the application will use to accept traffic (e.g. if the application uses HTTPS, specify 443; if the application uses HTTP, specify 80; etc.).

        ec2_traffic_port (str): Specify the port the EC2 instance will listen to. This is used also as the Target Group Health check configuration port. For example (str)if you EC2 is equipped with an Apache Tomcat, listening on port 8080, use this parameter to specify 8080. It's important to note that this is not port the final user will use to connect to the system, as the Load Balancer will be in-front of the EC2.This is the port that the load balancer will use to forward traffic to the EC2 (e.g. Tomcat uses port 8080, Node.js uses port 3000).

        ec2_health_check_path (str):  Specify the Target Group health check path to use to monitor the state of the EC2 instances. EC2 instances will be constantly monitored, performing requests to this path. The request must receive a successful response code to consider the EC2 healthy. Otherwise the EC2 will be terminated and regenerated. It must start with a slash "/"

        ec2_traffic_protocol (str): Specify the protocol the EC2 instance will listen to. This is used also as the Target Group Health check configuration protocol

        stickiness_cookie_duration_in_hours: (Optional | str) if provided sticky sessions will be configured for the Application Load Balancer.

        healthy_threshold_count: (Optional | int) The number of consecutive health checks successes required before considering an unhealthy target healthy. Default: 2

        unhealthy_threshold_count: (Optional | int) The number of consecutive health check failures required before considering the target unhealthy. For Application Load Balancers, the target is deregistered from the target group. For Network Load Balancers, the target is removed from the routing table. Default: 2

        interval_in_seconds: (Optional | int) The approximate amount of time, in seconds, between health checks of an individual target. Default: 6

        timeout_in_seconds: (Optional | int) The amount of time, in seconds, during which no response means a failed health check. Default: 5

        ssl_certificate_arn (str): In case you want to enable HTTPS for your stack, specify the SSL certificate ARN to use. This configuration will force the creation of 2 load balancer Listeners: one on port 443 that proxies to the Target Group, a second one on port 80 to redirect the traffic to port 443 and enforce HTTPS. In case the application implements HTTPS, specify the ARN of the SSL Certificate to use. You can find it in AWS Certificate Manager

        authorization_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        issuer (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        client_id (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        client_secret (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        user_info_endpoint (str): Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html

        token_endpoint (str):  Used with 'authorization_endpoint', 'client_id', 'client_secret', 'issuer', 'token_endpoint', 'user_info_endpoint'. Used to perform the OIDC Cognito integration with the Application Load balancer. More information https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancingv2-listenerrule-authenticateoidcconfig.html0

        will_create_tg(Bool): If the target group should be created or not. Default: True

        add_redirect_to_https_listener(Bool): If the HTTP to HTTPS listener should be created or not. Used only if protocol is HTTPS. Default: True

        allow_ingress_from_everyone(Bool): If the alb security group should allow ingress for everyone when load balancer is public. Default: True

        omit_cloudformation_template_outputs(bool): Omit the generation of CloudFormation template outputs. Default: false

        will_implement_cdn (str): Whether or not a CloudFront distribution should be deployed in front of the load balancer. Only applicable when an Application Load Balancer is in use

        cdn_domain_names ([str]): If "will_implement_cdn" is "True", it specifies the domain names to associate to the CloudFront distribution. Please make sure that tha provided domain names match the SSL certificate in use

        cdn_ssl_certificate_arn (str): If "will_implement_cdn" is "True" and you want to enable HTTPS for your CloudFront distribution, specify the SSL certificate ARN to use. NB: this certificate must be in North Virginia

        will_drop_invalid_header_fields (bool):  Indicates whether HTTP headers with invalid header fields are removed by the load balancer (True) or routed to targets (False). Default: False

    Returns:
        aws_fao_constructs.load_balancer.alb.Alb: the Application Load Balancer FAO construct that aggregates
        aws_fao_constructs.load_balancer.alb.Alb.alb: the Application Load Balancer aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer
        aws_fao_constructs.load_balancer.alb.Alb.tg: Target Group for the Application Load Balancer aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup
        aws_fao_constructs.load_balancer.alb.Alb.listener: the Application Load Balancer Listener aws_cdk.aws_elasticloadbalancingv2.ApplicationListener

    """

    @property
    def cloudfront_distribution(
        self,
    ) -> Union[_cloudfront.IDistribution, None]:
        """Returns the CloudFront distribution, if available

        Returns:
            aws_cloudfront.IDistribution: the Cloudfront distribution
        """
        return self._cloudfront_distribution

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name: str,
        environment: str,
        environments_parameters: dict,
        vpc: _ec2.IVpc,
        access_log_bucket_name: str = 'fao-elb-logs',
        security_group: _ec2.SecurityGroup = None,
        upstream_security_group: str = None,
        internet_facing: bool = False,
        load_balancer_name: str = None,
        use_cdn: Union[str, bool] = False,
        main_component_name: str = None,
        load_balancer_idle_timeout_in_seconds: int = None,
        dns_record: str = None,
        create_dns: str = 'True',
        traffic_port: str = '80',
        ec2_traffic_port: str = '80',
        ec2_health_check_path: str = '/',
        ec2_traffic_protocol: str = _alb.Protocol.HTTP,
        stickiness_cookie_duration_in_hours: str = None,
        healthy_threshold_count: int = 2,
        unhealthy_threshold_count: int = 2,
        interval_in_seconds: int = 6,
        timeout_in_seconds: int = 5,
        ssl_certificate_arn: str = None,
        authorization_endpoint: str = None,
        token_endpoint: str = None,
        issuer: str = None,
        client_id: str = None,
        client_secret: str = None,
        user_info_endpoint: str = None,
        will_create_tg: bool = True,
        add_redirect_to_https_listener: bool = True,
        allow_ingress_from_everyone: bool = True,
        will_implement_cdn: str = 'false',
        cdn_domain_names: [str] = [],
        cdn_ssl_certificate_arn: str = None,
        omit_cloudformation_template_outputs: bool = False,
        will_drop_invalid_header_fields: bool = False,
    ):
        super().__init__(scope, id + '-fao-construct')

        environment = normalize_environment_parameter(environment)
        is_production = environment == 'Production'
        aws_account = environments_parameters['accounts'][environment.lower()]

        create_cloudfront_distribution = (
            will_implement_cdn
            and isinstance(will_implement_cdn, str)
            and will_implement_cdn.lower() == 'true'
        )

        if create_cloudfront_distribution:
            # If CloudFront distribution will be created, the load balancer must be internet facing
            internet_facing = True

        self.id = id
        self.environments_parameters = environments_parameters
        self.environment = environment
        self.app_name = app_name
        self.vpc = vpc
        self.ssl_certificate_arn = ssl_certificate_arn
        self.is_https = ssl_certificate_arn is not None
        self.has_upstream = upstream_security_group is not None
        self.traffic_port = (
            _ec2.Port.tcp(int(traffic_port)) if traffic_port else None
        )
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.issuer = issuer
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_info_endpoint = user_info_endpoint
        self.main_component_name = (
            main_component_name if main_component_name else app_name
        )
        self.rule_priority = None
        self._client = None

        self.upstream_security_group_as_peer = (
            _ec2.SecurityGroup.from_security_group_id(
                self,
                'upstream_security_group_' + self.main_component_name,
                upstream_security_group,
                mutable=True,
            )
            if upstream_security_group
            else None
        )

        oicd_parameters = [
            authorization_endpoint,
            token_endpoint,
            issuer,
            client_id,
            client_secret,
            user_info_endpoint,
        ]
        self.has_oidc = all(oicd_parameters)
        if any(oicd_parameters) and not all(oicd_parameters):
            raise Exception(
                'OIDC configuration is not valid! If you aimed to configure OIDC listener please provide each of the params: authorization_endpoint, token_endpoint, issuer, client_id, client_secret, user_info_endpoint'
            )

        if load_balancer_name is None:
            load_balancer_name = id

        if load_balancer_idle_timeout_in_seconds is None:
            load_balancer_idle_timeout_in_seconds = '50'

        if use_cdn:
            security_group = self._cdn_security_group()
        else:
            path = '_'.join(self.node.path.split('/')[:-1])
            security_group = SecurityGroup(
                scope=self,
                id=f'{app_name}-{path}-sg',
                app_name=app_name,
                environment=environment,
                environments_parameters=environments_parameters,
                vpc=vpc,
                security_group_name=f'{app_name}_{path}_alb_sg',
            )
            if environment != 'Production':
                security_group.sg.add_ingress_rule(
                    peer=_ec2.Peer.ipv4('168.202.4.57/32'),
                    connection=_ec2.Port.tcp(int(traffic_port)),
                    description='From Security Scan tool',
                )

            if not create_cloudfront_distribution:
                if not internet_facing:
                    if self.traffic_port:
                        security_group.enable_fao_private_access(
                            self.traffic_port
                        )

                    # Enable access from App Proxy only if the Load Balancer is private if it is https and automatic redirect to https is enabled
                    if add_redirect_to_https_listener and self.is_https:
                        security_group.enable_fao_private_access(
                            _ec2.Port.tcp(80)
                        )

                    if self.has_upstream:
                        security_group.sg.add_ingress_rule(
                            peer=self.upstream_security_group_as_peer,
                            connection=_ec2.Port.tcp(int(traffic_port)),
                            description='From upstream',
                        )
                else:
                    # Load balancer is public
                    if self.has_upstream:
                        if add_redirect_to_https_listener:
                            security_group.sg.add_ingress_rule(
                                peer=self.upstream_security_group_as_peer,
                                connection=_ec2.Port.tcp(80)
                                if self.is_https
                                else _ec2.Port.tcp(int(traffic_port)),
                                description='Upstream to HTTPS'
                                if self.is_https
                                else 'From upstream',
                            )
                        else:
                            security_group.sg.add_ingress_rule(
                                peer=self.upstream_security_group_as_peer,
                                connection=_ec2.Port.tcp(int(traffic_port)),
                                description='From Upstream',
                            )
                    else:
                        # Public and no upstream
                        if self.is_https:
                            if (
                                add_redirect_to_https_listener
                                and allow_ingress_from_everyone
                            ):
                                security_group.sg.add_ingress_rule(
                                    peer=_ec2.Peer.any_ipv4(),
                                    connection=_ec2.Port.tcp(80),
                                    description='Everyone to HTTP',
                                )
                            if allow_ingress_from_everyone:
                                security_group.sg.add_ingress_rule(
                                    peer=_ec2.Peer.any_ipv4(),
                                    connection=_ec2.Port.tcp(443)
                                    if not traffic_port
                                    else _ec2.Port.tcp(int(traffic_port)),
                                    description='Everyone to HTTPS',
                                )
                        else:
                            if allow_ingress_from_everyone:
                                security_group.sg.add_ingress_rule(
                                    peer=_ec2.Peer.any_ipv4(),
                                    connection=_ec2.Port.tcp(80)
                                    if not traffic_port
                                    else _ec2.Port.tcp(int(traffic_port)),
                                    description='Everyone',
                                )
            else:
                # Only allow access from CloudFront
                security_group.sg.add_ingress_rule(
                    peer=_ec2.Peer.prefix_list(
                        self.environments_parameters['networking'][
                            'prefixlists_cloudfront_origin_facing'
                        ]
                    ),
                    connection=_ec2.Port.tcp(int(traffic_port)),
                    description='Allow CloudFront access',
                )

        self.security_group = security_group.sg

        self.alb = _alb.ApplicationLoadBalancer(
            scope,
            id,
            load_balancer_name=load_balancer_name,
            vpc=vpc,
            internet_facing=internet_facing,
            idle_timeout=Duration.seconds(
                int(load_balancer_idle_timeout_in_seconds)
            ),
            security_group=self.security_group,
            deletion_protection=is_production,
            drop_invalid_header_fields=will_drop_invalid_header_fields,
        )

        # Enable access from App Proxy if the Load Balancer is private
        if internet_facing is False:
            aws_account = environments_parameters['accounts'][
                environment.lower()
            ]
            app_proxy_security_group = (
                _ec2.SecurityGroup.from_security_group_id(
                    self,
                    'upstream_security_group_app_proxy_'
                    + self.main_component_name,
                    aws_account['app_proxy_security_group'],
                    mutable=False,
                )
            )
            self.alb.add_security_group(app_proxy_security_group)

        # Enable logging
        self._alb_logs_bucket = _s3.Bucket.from_bucket_name(
            scope=self,
            id='alb_logs_bucket',
            bucket_name=access_log_bucket_name,
        )

        self.alb.log_access_logs(self._alb_logs_bucket, prefix=app_name)

        # Apply mandatory tags
        Tags.of(self.alb).add('ApplicationName', app_name.lower().strip())
        Tags.of(self.alb).add('Environment', environment)

        # Create DNS record
        if not is_production and create_dns.lower() == 'true':
            hosted_zone_id = aws_account['route53_hosted_zone_id']
            domain_name = aws_account['route53_domain_name']

            dns_record = dns_record if dns_record else app_name
            self.route53_zone = (
                route53.PrivateHostedZone.from_hosted_zone_attributes(
                    self,
                    f'PrivateHostedZone{dns_record}',
                    hosted_zone_id=hosted_zone_id,
                    zone_name=domain_name,
                )
            )

            route53.ARecord(
                self,
                f'ALBAliasRecord{dns_record}',
                zone=self.route53_zone,
                target=route53.RecordTarget.from_alias(
                    route53_targets.LoadBalancerTarget(self.alb)
                ),
                record_name=f'{dns_record}.{domain_name}',
            )

        self.tg = None
        if will_create_tg:
            self.tg = self._create_tg(
                id=main_component_name,
                ec2_traffic_port=ec2_traffic_port,
                ec2_health_check_path=ec2_health_check_path,
                protocol=ec2_traffic_protocol,
                stickiness_cookie_duration_in_hours=stickiness_cookie_duration_in_hours,
                healthy_threshold_count=healthy_threshold_count,
                unhealthy_threshold_count=unhealthy_threshold_count,
                interval_in_seconds=interval_in_seconds,
                timeout_in_seconds=timeout_in_seconds,
            )

        self.listener = None
        if not self.is_https:
            self.add_http_listener()
        else:
            if add_redirect_to_https_listener:
                self.add_http_redirect_to_https_listener()
            self.certificate = _certificate.Certificate.from_certificate_arn(
                self, 'https_certificate', certificate_arn=ssl_certificate_arn
            )
            if not self.has_oidc:
                self.add_https_listener()
            else:
                self.add_https_oidc_listener()

        # Create CloudFront distribution
        if create_cloudfront_distribution:
            self._cloudfront_distribution = _cloudfront.Distribution(
                self,
                f'distribution_{self.app_name}_{self.main_component_name}',
                default_behavior=_cloudfront.BehaviorOptions(
                    origin=_cloudfront_origins.LoadBalancerV2Origin(self.alb),
                    compress=True,
                    viewer_protocol_policy=_cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                    allowed_methods=_cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                    cache_policy=_cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=_cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                certificate=_certificate.Certificate.from_certificate_arn(
                    self,
                    'https_certificate_cdn',
                    certificate_arn=cdn_ssl_certificate_arn
                    if cdn_ssl_certificate_arn
                    else aws_account[
                        'ssl_certificate_star_fao_org_arn_north_virginia'
                    ],
                ),
                price_class=_cloudfront.PriceClass.PRICE_CLASS_100,
                domain_names=cdn_domain_names,
            )

    def add_https_listener(self) -> None:
        if self.tg:
            self.listener = self.alb.add_listener(
                'is_https',
                port=int(self.traffic_port.to_string()),
                protocol=_alb.ApplicationProtocol.HTTPS,
                certificates=[self.certificate],
                default_target_groups=[self.tg],
                open=False,
                ssl_policy=_alb.SslPolicy.FORWARD_SECRECY_TLS12_RES,
            )
        else:
            default_action = _alb.ListenerAction.fixed_response(
                200, message_body=f'{self.app_name} default landing page'
            )
            self.listener = self.alb.add_listener(
                id='is_https',
                port=int(self.traffic_port.to_string()),
                open=False,
                protocol=_alb.ApplicationProtocol.HTTPS,
                certificates=[self.certificate],
                ssl_policy=_alb.SslPolicy.FORWARD_SECRECY_TLS12_RES,
                default_action=default_action,
            )

    def add_https_oidc_listener(self) -> None:
        listener_default_action = _alb.ListenerAction.forward(
            target_groups=[self.tg]
        )

        # OIDC action: authenticate with Cognito and concatenate the forward
        oidc_listener_action = _alb.ListenerAction.authenticate_oidc(
            authorization_endpoint=self.authorization_endpoint,
            token_endpoint=self.token_endpoint,
            issuer=self.issuer,
            client_id=self.client_id,
            client_secret=SecretValue(protected_value=self.client_secret),
            user_info_endpoint=self.user_info_endpoint,
            next=listener_default_action,
        )

        # Create listener
        self.listener = self.alb.add_listener(
            'is_https',
            port=int(self.traffic_port.to_string()),
            open=False,
            protocol=_alb.ApplicationProtocol.HTTPS,
            certificates=[self.certificate],
            default_action=oidc_listener_action,
            ssl_policy=_alb.SslPolicy.FORWARD_SECRECY_TLS12_RES,
        )

    def add_http_listener(self) -> None:
        if self.tg:
            self.listener = self.alb.add_listener(
                id='is_not_https',
                port=int(self.traffic_port.to_string()),
                open=False,
                protocol=_alb.ApplicationProtocol.HTTP,
                default_target_groups=[self.tg] if self.tg else None,
            )
        else:
            default_action = _alb.ListenerAction.fixed_response(
                200, message_body=f'{self.app_name} default landing page'
            )
            self.listener = self.alb.add_listener(
                id='is_not_https',
                port=int(self.traffic_port.to_string()),
                open=False,
                protocol=_alb.ApplicationProtocol.HTTP,
                default_action=default_action,
            )

    def add_http_redirect_to_https_listener(self) -> None:
        self.listener = self.alb.add_listener(
            id='redirect_to_https',
            port=80,
            open=False,
            protocol=_alb.ApplicationProtocol.HTTP,
            default_action=_alb.ListenerAction.redirect(
                host='#{host}',
                path='/#{path}',
                port=self.traffic_port.to_string(),
                protocol='HTTPS',
                query='#{query}',
                permanent=True,
            ),
        )

    def _create_tg(
        self,
        id: str,
        ec2_traffic_port: str,
        ec2_health_check_path: str,
        healthy_threshold_count: int,
        interval_in_seconds: int,
        timeout_in_seconds: int,
        unhealthy_threshold_count: int,
        protocol: _alb.Protocol = _alb.Protocol.HTTP,
        stickiness_cookie_duration_in_hours: str = None,
    ) -> _alb.ApplicationTargetGroup:
        tg = _alb.ApplicationTargetGroup(
            self,
            id + '_alb_tg',
            port=int(ec2_traffic_port),  # Must be a int
            protocol=_alb.ApplicationProtocol.HTTP
            if protocol == _alb.Protocol.HTTP
            else _alb.ApplicationProtocol.HTTPS,
            vpc=self.vpc,
            target_type=_alb.TargetType.INSTANCE,
            target_group_name=f'{self.app_name}-{id}-{ec2_traffic_port}'.replace(
                '_', '-'
            )[
                :32
            ],
            stickiness_cookie_duration=Duration.hours(
                int(stickiness_cookie_duration_in_hours)
            )
            if stickiness_cookie_duration_in_hours
            else None,
        )
        tg.configure_health_check(
            enabled=True,
            healthy_http_codes='200-399',
            healthy_threshold_count=healthy_threshold_count,
            interval=Duration.seconds(interval_in_seconds),
            path=ec2_health_check_path,
            port=ec2_traffic_port,
            protocol=protocol,
            timeout=Duration.seconds(timeout_in_seconds),
            unhealthy_threshold_count=unhealthy_threshold_count,
        )

        # Apply mandatory tags
        Tags.of(tg).add('ApplicationName', self.app_name.lower().strip())
        Tags.of(tg).add('Environment', self.environment)

        return tg

    def _cdn_security_group(self) -> _ec2.SecurityGroup:
        cdn_security_group = SecurityGroup(
            scope=self,
            id='alb_secg_cdn',
            app_name=self.app_name,
            environment=self.environment,
            environments_parameters=self.environments_parameters,
            security_group_name=f'{self.app_name}_{self.main_component_name}_alb_sg_cdn',
            vpc=self.vpc,
        )

        fao_networks = self.environments_parameters['networking']
        cdn_security_group.sg.add_ingress_rule(
            peer=_ec2.Peer.prefix_list(
                fao_networks['prefixlists_cloudflare_ipv4']
            ),
            connection=self.traffic_port,
            description='Cloudflare IPv4',
        )

        cdn_security_group.sg.add_ingress_rule(
            peer=_ec2.Peer.prefix_list(
                fao_networks['prefixlists_cloudflare_ipv6']
            ),
            connection=self.traffic_port,
            description='Cloudflare IPv6',
        )
        return cdn_security_group

    def _parameter_store_rule_priority_path(self) -> str:
        return f'/{self.app_name}/alb/{self.id}/rule_priority'

    def _initialize_ssm_client(self) -> None:
        if not self._client:
            import boto3

            session = boto3.session.Session()
            self._client = session.client('ssm')
        return self._client

    def _get_ssm_rule_priority(self) -> int:
        self._initialize_ssm_client()
        try:
            return self._client.get_parameter(
                Name=self._parameter_store_rule_priority_path(),
                WithDecryption=False,
            )
        except ClientError as e:
            return None

    def get_safe_rule_priority(self) -> int:
        """
        Rule priority collisions will happen when trying to insert any rule with the same priority of the existing one,
        this makes difficult Alb listener rule managing. This function is a counter that will return a priority number
        safe to use for listener rules. If adds an offset to the counter that flaps between 1 and 100 on each deploy
        based on the previous one saved on parameter store

        Returns: (int) A free priority number for a listener rule

        """
        if self.rule_priority:
            self.rule_priority += 1
            return self.rule_priority
        else:
            ssm_rule_priority = self._get_ssm_rule_priority()
            if not ssm_rule_priority:
                self.rule_priority = 200
            else:
                self.rule_priority = (
                    1
                    if ssm_rule_priority.get('Parameter').get('Value') != '1'
                    else 100
                )
            _ssm.StringParameter(
                scope=self,
                id='alb_rule_priority_index',
                parameter_name=self._parameter_store_rule_priority_path(),
                string_value=str(self.rule_priority),
            )
            return self.rule_priority
