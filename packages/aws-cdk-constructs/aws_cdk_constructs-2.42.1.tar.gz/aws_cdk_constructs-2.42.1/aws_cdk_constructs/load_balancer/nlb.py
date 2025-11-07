from constructs import Construct
from aws_cdk_constructs.utils import normalize_environment_parameter

from aws_cdk import (
    aws_elasticloadbalancingv2 as _alb,
    aws_ec2 as _ec2,
    Tags,
    aws_route53 as _route53,
    aws_route53_targets as _route53_targets,
    Duration,
)


class Nlb(Construct):
    """
    The FAO CDK Nlb Construct creates AWS Network Load Balancer resources.

    The construct automatically enables the following main features:

    -	Creates private and internet-facing AWS Network Load Balancers with custom configurations;
    -	Private DNS record creation for non-Production environments;
    -	AWS Target Group creation and health-check configuration;

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:
        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliance. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        main_component_name (str): This is just a metadata. Textually specify the component the EC2 instance will host (e.g. tomcat, drupal, ...)

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        vpc (_ec2.IVpc): The VPC in which the load balancer will be created

        network_load_balancer_ip_1 (Optional | str): nlb ip 1

        network_load_balancer_ip_2 (Optional | str): nlb ip 2

        network_load_balancer_subnet_1 (Optional | str): private subnet 1

        network_load_balancer_subnet_2 (Optional | str): private subnet 2

        ec2_traffic_port (str): Specify the port the EC2 instance will listen to. This is used also as the Target Group Health check configuration port. For example (str)if you EC2 is equipped with an Apache Tomcat, listening on port 8080, use this parameter to specify 8080. It's important to note that this is not port the final user will use to connect to the system, as the Load Balancer will be in-front of the EC2.This is the port that the load balancer will use to forward traffic to the EC2 (e.g. Tomcat uses port 8080, Node.js uses port 3000).

        load_balancer_name (str): the load balancer name

        healthy_threshold_count: (Optional | int) The number of consecutive health checks successes required before considering an unhealthy target healthy. Default: 2

        unhealthy_threshold_count: (Optional | int) The number of consecutive health check failures required before considering the target unhealthy. For Application Load Balancers, the target is deregistered from the target group. For Network Load Balancers, the target is removed from the routing table. Default: 2

        interval:(Optional | int) The approximate amount of time, in seconds, between health checks of an individual target. Default: 6

        timeout: (Optional | int) The amount of time, in seconds, during which no response means a failed health check. Default: 5

         dns_record: (Optional | str) The DNS record associated to the Load Balancer. This is applied only in Development and QA environment. If multiple Load Balancers are included in the stack, the parameter is mandatory (Default is app_name)

         create_dns: (Optional | str) to enable/disable dns creation - format Boolean (`true`, `false`). Default: true

    Return:
        aws_fao_constructs.load_balancer.nlb.Nlb: The newly created network load balancer
        aws_fao_constructs.load_balancer.alb.Nlb.nlb: the network Load Balancer aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer
        aws_fao_constructs.load_balancer.alb.Nlb.tg: Target Group for the Load Balancer aws_cdk.aws_elasticloadbalancingv2.NetworkTargetGroup
        aws_fao_constructs.load_balancer.alb.Nlb.listener: the Load Balancer Listener aws_cdk.aws_elasticloadbalancingv2.NetworkListener

    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name: str,
        main_component_name: str,
        environment: str,
        environments_parameters: dict,
        vpc: _ec2.IVpc,
        network_load_balancer_ip_1: str,
        network_load_balancer_ip_2: str,
        network_load_balancer_subnet_1: str,
        network_load_balancer_subnet_2: str,
        ec2_traffic_port: str,
        load_balancer_name: str = None,
        healthy_threshold_count: int = 2,
        unhealthy_threshold_count: int = 2,
        interval: int = 30,
        timeout: int = 10,
        dns_record: str = None,
        create_dns: str = 'True',
    ) -> None:

        super().__init__(scope, id + '-fao-construct')

        self.environment = environment
        self.app_name = app_name
        self.vpc = vpc

        environment = normalize_environment_parameter(environment)
        is_production = environment == 'Production'
        aws_account = environments_parameters['accounts'][environment.lower()]

        if load_balancer_name is None:
            load_balancer_name = id

        nlb = _alb.NetworkLoadBalancer(
            scope,
            id + '_nlb',
            load_balancer_name=load_balancer_name,
            cross_zone_enabled=True,
            vpc=vpc,
            deletion_protection=is_production,
            internet_facing=False,
        )
        cfnNlb = nlb.node.default_child
        cfnNlb.add_deletion_override('Properties.Subnets')
        cfnNlb.add_property_override(
            property_path='SubnetMappings',
            value=[
                {
                    'SubnetId': network_load_balancer_subnet_1,
                    'PrivateIPv4Address': network_load_balancer_ip_1,
                },
                {
                    'SubnetId': network_load_balancer_subnet_2,
                    'PrivateIPv4Address': network_load_balancer_ip_2,
                },
            ],
        )

        # Create DNS record
        if not is_production and create_dns.lower() == 'true':
            hosted_zone_id = aws_account['route53_hosted_zone_id']
            domain_name = aws_account['route53_domain_name']

            dns_record = dns_record if dns_record else app_name
            route53_zone = (
                _route53.PrivateHostedZone.from_hosted_zone_attributes(
                    self,
                    f'PrivateHostedZone{dns_record}',
                    hosted_zone_id=hosted_zone_id,
                    zone_name=domain_name,
                )
            )

            _route53.ARecord(
                self,
                f'ALBAliasRecord{dns_record}',
                zone=route53_zone,
                target=_route53.RecordTarget.from_alias(
                    _route53_targets.LoadBalancerTarget(nlb)
                ),
                record_name=f'{dns_record}.{domain_name}',
            )
        self.nlb = nlb
        self.tg = self._create_tg(
            id=main_component_name,
            ec2_traffic_port=ec2_traffic_port,
            healthy_threshold_count=healthy_threshold_count,
            unhealthy_threshold_count=unhealthy_threshold_count,
            interval=interval,
            timeout=timeout,
        )
        self.listener = self.nlb.add_listener(
            'instance_nlb_listener',
            port=int(ec2_traffic_port),
            protocol=_alb.Protocol.TCP,
            default_target_groups=[self.tg],
        )

    def _create_tg(
        self,
        id: str,
        ec2_traffic_port: str,
        healthy_threshold_count: int,
        unhealthy_threshold_count: int,
        interval: int,
        timeout: int,
    ) -> _alb.NetworkTargetGroup:
        nlb_tg_hc = _alb.HealthCheck(
            healthy_threshold_count=healthy_threshold_count,
            interval=Duration.seconds(interval),
            port=ec2_traffic_port,
            protocol=_alb.Protocol.TCP,
            unhealthy_threshold_count=unhealthy_threshold_count,
            timeout=Duration.seconds(timeout),
        )

        nlb_target_group = _alb.NetworkTargetGroup(
            self,
            id + '_nlb_tg',
            port=int(ec2_traffic_port),
            protocol=_alb.Protocol.TCP,
            health_check=nlb_tg_hc,
            target_type=_alb.TargetType.INSTANCE,
            vpc=self.vpc,
        )

        Tags.of(nlb_target_group).add('ApplicationName', self.app_name)
        Tags.of(nlb_target_group).add('Environment', self.environment)

        self.health_check = nlb_tg_hc
        return nlb_target_group
