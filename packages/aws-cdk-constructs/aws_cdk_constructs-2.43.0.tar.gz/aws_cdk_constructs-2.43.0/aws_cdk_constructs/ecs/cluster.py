from __future__ import annotations

from aws_cdk import (
    aws_ecs as _ecs,
    aws_ec2 as _ec2,
    aws_iam as _iam,
    aws_route53 as _route53,
    aws_cloudwatch as _cloudwatch,
    aws_elasticloadbalancingv2 as _elb,
    aws_autoscaling as _autoscaling,
    aws_secretsmanager as _secretsmanager,
    Duration,
    Tags,
)
from constructs import Construct
from typing import List, Optional, TYPE_CHECKING, Dict

from aws_cdk_constructs.load_balancer import Alb

if TYPE_CHECKING:
    from .microservice import ECSMicroservice


class ECSCluster(Construct):
    """
    The FAO CDK ECSCluster Construct creates ECS-based (Docker) solutions.

    The construct automatically enables the following features:

    -	Creates AWS ECS Clusters;
    -	Enable AWS ECS Container Insights;
    -	Conditionally create a Load Balancer leveraging the FAO CDK Load Balancer construct;
    -	Expose methods to add FAO CDK ECSMicroservice instances to the cluster;
    -	Conditionally tracking of ECS cluter metrics in the FAO CloudWatch dashboard;

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:
            scope (Construct): Parent construct

            id (str): the logical id of the newly created resource

            environment (str): The environment the cluster is being created in. This is used to determine the VPC to use

            environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

            domain_name (str): every cluster has associated a route53 hosted zone, where entries will be created to

            hosted_zone (aws_route53.IHostedZone): Route53 hosted zone where the cluster will create entries for the microservices

            app_name (str): The name of the application that will be deployed in the cluster,

            create_alb (Optional - bool): Whether to create the alb or not. Default is true

            create_alb_dns (Optional - bool): Whether to create the alb dns or not. Default is false

            track (Optional - bool): When set to true it creates a CloudWatch dashboard than can be rendered using the method render_widgets() once all the ms have been added to the cluster

            target_priority (Optional - int): [Deprecated, this is now automatically handled within the cluster] Default 1. Listener rule priority start in the target groups, when a ms is added it registers itself with this priority and increases the counter. When removing services from the cluster it may fail with priority collision, setting this counter to different range (e.g. 100) will fix the error.

            internet_facing (Optional - bool): Whether the Alb should be internet-facing or not

            ssl_certificate_arn (str):  ARN of the SSL certificate to be used by the ALB listener overwriting the default one for the environment

            use_cdn (Optional - bool): Add cloudflare IPs to the ALB security group

            load_balancer_idle_timeout (Optional int): Sets the default timeout for the ALB in seconds. Defaults to 50s in ALB construct

            ec2_enable (Optional - bool): Enables a EC2 capacity provider in the cluster.

            ec2_instance_type (Optional - str): The instance type to be used by the EC2 capacity provider.

            ec2_desired_capacity (Optional - int): The desired capacity of the EC2 capacity provider.

            ec2_max_capacity (Optional - int): The max capacity of the EC2 capacity provider.

            ec2_tag_scheduler_uptime (Optional - str): The tag to be used to filter the EC2 instances to be used by the scheduler.

            ec2_tag_scheduler_uptime_days (Optional - str): The tag to be used to filter the EC2 instances to be used by the scheduler.

            ec2_tag_scheduler_skip (Optional - str): The tag to be used to filter the EC2 instances to be used by the scheduler.

            will_drop_invalid_headers (Optional | str): Indicates whether HTTP headers with invalid header fields are removed by the load balancer ('true') or routed to targets ('false'). Default: false
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        environments_parameters: Dict,
        app_name: str,
        environment: str,
        domain_name: str = 'example.com',
        hosted_zone: Optional[_route53.IHostedZone] = None,
        create_alb: Optional[bool] = True,
        create_alb_dns: Optional[bool] = False,
        track: Optional[bool] = False,
        target_priority: Optional[int] = 1,
        internet_facing: Optional[bool] = False,
        use_cdn: Optional[bool] = False,
        ssl_certificate_arn: Optional[str] = None,
        load_balancer_idle_timeout: Optional[int] = None,
        ec2_enable: Optional[bool] = False,
        ec2_instance_type: Optional[str] = None,
        ec2_desired_capacity: Optional[int] = None,
        ec2_max_capacity: Optional[int] = None,
        ec2_tag_scheduler_uptime: Optional[str] = '08:00-18:00',
        ec2_tag_scheduler_uptime_days: Optional[str] = '1-2-3-4-5',
        ec2_tag_scheduler_skip: Optional[str] = 'False',
        will_drop_invalid_headers: str = 'False',
    ) -> None:
        self.id = id
        self.scope = scope
        self.environments_parameters = environments_parameters
        self.microservices: List[ECSMicroservice] = []
        self.hosted_zone = hosted_zone
        self.domain_name = domain_name
        self.app_name = app_name
        self.aws_account = self.environments_parameters['accounts'][
            environment.lower()
        ]
        self.vpc = self._get_vpc()
        self.target_priority = target_priority
        self.environment = environment
        ssl_certificate_arn = ssl_certificate_arn or self.aws_account.get(
            'ssl_certificate_star_fao_org_arn'
        )
        self.create_alb = create_alb

        self.ec2_enabled = all(
            [
                ec2_enable,
                ec2_max_capacity,
                ec2_desired_capacity,
                ec2_instance_type,
            ]
        )
        self.ec2_instance_type = (ec2_instance_type,)
        self.ec2_max_capacity = (ec2_max_capacity,)
        self.ec2_desired_capacity = ec2_desired_capacity

        super().__init__(scope, id)

        create_alb_dns = 'True' if create_alb_dns else 'False'

        if track:
            self.dashboard = self._get_dashboard()

        self._create_cluster()
        if create_alb:
            drop_invalid_headers = (
                will_drop_invalid_headers
                and isinstance(will_drop_invalid_headers, str)
                and will_drop_invalid_headers.lower() == 'true'
            )

            path = '_'.join(self.node.path.split('/')[:-1])[:28]

            self.alb = Alb(
                scope=self.scope,
                id=f'{path}-alb',
                app_name=self.app_name,
                environment=environment,
                environments_parameters=self.environments_parameters,
                ssl_certificate_arn=ssl_certificate_arn,
                vpc=self.vpc,
                access_log_bucket_name='fao-elb-logs',
                will_create_tg=False,
                traffic_port='443',
                create_dns=create_alb_dns,
                internet_facing=internet_facing,
                use_cdn=use_cdn,
                load_balancer_idle_timeout_in_seconds=load_balancer_idle_timeout,
                will_drop_invalid_header_fields=drop_invalid_headers,
            )
        else:
            self.alb = None

        if self.ec2_enabled:
            self.ecs_sg = _ec2.SecurityGroup(
                self, f'{app_name}-sg', vpc=self.vpc
            )
            self.ecs_sg.add_ingress_rule(
                peer=self.alb.security_group,
                connection=_ec2.Port.tcp_range(
                    start_port=32768, end_port=65535
                ),
            )
            self._ec2_role = _iam.Role(
                self,
                'asg_role',
                description=app_name + '_' + '_ec2_role',
                assumed_by=_iam.ServicePrincipal('ec2.amazonaws.com'),
                managed_policies=[
                    # AWS managed policy to allow sending logs and custom metrics to CloudWatch
                    _iam.ManagedPolicy.from_aws_managed_policy_name(
                        'CloudWatchAgentServerPolicy'
                    ),
                    # AWS managed policy to allow Session Manager console connections to the EC2 instance
                    _iam.ManagedPolicy.from_aws_managed_policy_name(
                        'AmazonSSMManagedInstanceCore'
                    ),
                ],
                role_name=app_name + '_' + '_ec2_role',
            )

            user_data = _ec2.UserData.for_linux()
            user_data.add_commands(
                'yum -y install docker',
                'service docker start',
                'curl -O https://s3.eu-west-1.amazonaws.com/amazon-ecs-agent-eu-west-1/amazon-ecs-init-latest.x86_64.rpm',
                'sudo yum localinstall -y amazon-ecs-init-latest.x86_64.rpm',
                f"echo 'ECS_CLUSTER={self.cluster.cluster_name}' >> /etc/ecs/ecs.config",
                "echo 'ECS_ENABLE_TASK_IAM_ROLE=true' >> /etc/ecs/ecs.config",
                'echo \'ECS_AVAILABLE_LOGGING_DRIVERS=["awslogs"]\' >> /etc/ecs/ecs.config',
                'cat /etc/ecs/ecs.config',
                'service ecs start',
                'yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm',
                'sudo systemctl status amazon-ssm-agent',
                'ssm-cli get-diagnostics --output table',
            )
            machine_image = _ec2.GenericLinuxImage(
                {'eu-west-1': self._get_ami_id(f'{self.id}-ami-id')}
            )

            if not machine_image:
                raise TypeError(
                    f'Impossible to determine the AMI ID for environment: {self.environment}'
                )
            launch_template = _ec2.LaunchTemplate(
                self,
                f'{app_name}-lt',
                detailed_monitoring=True,
                machine_image=machine_image,
                role=self._ec2_role,
                user_data=user_data,
                security_group=self.ecs_sg,
                instance_type=_ec2.InstanceType(ec2_instance_type),
            )
            auto_scaling_group = _autoscaling.AutoScalingGroup(
                self,
                f'{app_name}-asg',
                vpc=self.vpc,
                allow_all_outbound=True,
                desired_capacity=ec2_desired_capacity,
                max_capacity=ec2_max_capacity,
                launch_template=launch_template,
            )

            capacity_provider = _ecs.AsgCapacityProvider(
                self,
                f'{app_name}-AsgCapacityProvider',
                auto_scaling_group=auto_scaling_group,
            )
            self.cluster.add_asg_capacity_provider(capacity_provider)
            Tags.of(auto_scaling_group).add(
                'SchedulerSkip',
                ec2_tag_scheduler_skip,
                apply_to_launched_instances=True,
            )
            Tags.of(auto_scaling_group).add(
                'SchedulerUptime',
                ec2_tag_scheduler_uptime,
                apply_to_launched_instances=True,
            )
            Tags.of(auto_scaling_group).add(
                'SchedulerUptimeDays',
                ec2_tag_scheduler_uptime_days,
                apply_to_launched_instances=True,
            )

    def _get_ami_id(self, id):
        ami_secret_arn = self.environments_parameters.get('common').get(
            'al2023_x86_64_ami_secret_arn'
        )
        # Determine the Image Architecture to retrieve the correspondent secret ID
        # Get the AMI secret as json
        secret_obj = _secretsmanager.Secret.from_secret_complete_arn(
            scope=self,
            id=self.id + '_ami_secret' + id,
            secret_complete_arn=ami_secret_arn,
        )
        # Normalize the environment name
        # We only has three development stages (development, qa, production)
        # Any other environment will use the production version of the AMI (like Shared Services, which is a production environment)
        development_stages = ['development', 'qa', 'production']
        ami_secret_environment = ('production', self.environment)[
            self.environment.lower in development_stages
        ]

        ami_secret_environment_lower = ami_secret_environment.lower()
        # Get the AMI id correspondent to the selected environment, as CDK token
        ec2_ami_id = secret_obj.secret_value_from_json(
            f'{ami_secret_environment_lower}/ami_id'
        ).unsafe_unwrap()  # Unsafe unwrap as we accept that the value is part of the cloudformation template
        if not ec2_ami_id:
            raise TypeError(
                f'Impossible to retrieve the AMI ID from secrets manager for environment: {self.environment}'
            )
        return ec2_ami_id

    def _get_vpc(self) -> _ec2.IVpc:
        return _ec2.Vpc.from_lookup(
            self.scope, self.id + 'VPC', vpc_id=self.aws_account.get('vpc')
        )

    def _create_cluster(self) -> None:
        self.cluster = _ecs.Cluster(
            scope=self.scope,
            id=self.id + '_ecs',
            vpc=self.vpc,
            container_insights=True,
        )

    def register_ms(self, microservice: ECSMicroservice) -> None:
        """Adds a ECSMicroservice instance to the list of hosted services in the cluster"""
        self.microservices.append(microservice)

    def _get_dashboard(self) -> _cloudwatch.Dashboard:
        path = '_'.join(self.node.path.split('/')[:-1])
        return (
            self.scope.node.try_find_child(f'{self.app_name}-{path}-dashboard')
            or self._create_dashboard()
        )

    def _create_dashboard(self) -> _cloudwatch.Dashboard:
        path = '_'.join(self.node.path.split('/')[:-1])
        return _cloudwatch.Dashboard(
            self.scope,
            f'{self.app_name}-{path}-dashboard',
            dashboard_name=f'{self.app_name}-{path}',
            end='end',
            period_override=_cloudwatch.PeriodOverride.AUTO,
            start='start',
        )

    def render_widgets(self) -> None:
        path = '_'.join(self.node.path.split('/')[:-1])
        self.dashboard = self._get_dashboard()

        self.dashboard.add_widgets(
            _cloudwatch.TextWidget(
                markdown=f'# {self.app_name} {path}', width=24
            )
        )

        http_codes_200 = []
        http_codes_300 = []
        http_codes_400 = []
        http_codes_500 = []
        alb_response_time = []
        cpu = []
        memory = []
        task_count = []
        for ms in self.microservices:
            if hasattr(ms, 'target_group'):
                alb_response_time.append(
                    ms.target_group.metric_target_response_time(label=ms.id)
                )
                http_codes_200.append(
                    ms.target_group.metric_http_code_target(
                        code=_elb.HttpCodeTarget.TARGET_2XX_COUNT,
                        statistic='Avg',
                        period=Duration.minutes(1),
                        label=f'2xx {ms.id}',
                    )
                )
                http_codes_300.append(
                    ms.target_group.metric_http_code_target(
                        code=_elb.HttpCodeTarget.TARGET_3XX_COUNT,
                        statistic='Avg',
                        period=Duration.minutes(1),
                        label=f'{ms.id}',
                    )
                )
                http_codes_400.append(
                    ms.target_group.metric_http_code_target(
                        code=_elb.HttpCodeTarget.TARGET_4XX_COUNT,
                        statistic='Avg',
                        period=Duration.minutes(1),
                        label=f'{ms.id}',
                    )
                )
                http_codes_500.append(
                    ms.target_group.metric_http_code_target(
                        code=_elb.HttpCodeTarget.TARGET_5XX_COUNT,
                        statistic='Avg',
                        period=Duration.minutes(1),
                        label=f'{ms.id}',
                    )
                )

            task_count.append(
                _cloudwatch.Metric(
                    metric_name='RunningTaskCount',
                    namespace='ECS/ContainerInsights',
                    dimensions_map={
                        'ClusterName': self.cluster.cluster_name,
                        'ServiceName': ms.service.service_name,
                    },
                    period=Duration.minutes(1),
                    statistic='Average',
                    label=ms.id,
                )
            )
            ms_id_normalized = str(ms.id).replace('-', '')
            cpu.append(
                _cloudwatch.MathExpression(
                    label=ms.id,
                    expression=f'100*(used_{ms_id_normalized}/reserved_{ms_id_normalized})',
                    using_metrics={
                        f'used_{ms_id_normalized}': _cloudwatch.Metric(
                            metric_name='CpuUtilized',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster_name,
                                'ServiceName': ms.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                            label=f'{ms.id} used',
                        ),
                        f'reserved_{ms_id_normalized}': _cloudwatch.Metric(
                            metric_name='CpuReserved',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster_name,
                                'ServiceName': ms.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                            label=f'{ms.id} reserved',
                        ),
                    },
                )
            )

            memory.append(
                _cloudwatch.MathExpression(
                    label=ms.id,
                    expression=f'100*(used_{ms_id_normalized}/reserved_{ms_id_normalized})',
                    using_metrics={
                        f'used_{ms_id_normalized}': _cloudwatch.Metric(
                            metric_name='MemoryUtilized',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster_name,
                                'ServiceName': ms.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                            label=f'{ms.id} used',
                        ),
                        f'reserved_{ms_id_normalized}': _cloudwatch.Metric(
                            metric_name='MemoryReserved',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster_name,
                                'ServiceName': ms.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                            label=f'{ms.id} reserved',
                        ),
                    },
                )
            )

        self.dashboard.add_widgets(
            _cloudwatch.GraphWidget(
                title='ALB response times', left=alb_response_time, width=24
            )
        )

        self.dashboard.add_widgets(
            _cloudwatch.GraphWidget(
                title='2xx count', left=http_codes_200, width=12
            ),
            _cloudwatch.GraphWidget(
                title='3xx count', left=http_codes_300, width=12
            ),
            _cloudwatch.GraphWidget(
                title='4xx count', left=http_codes_400, width=12
            ),
            _cloudwatch.GraphWidget(
                title='5xx count', left=http_codes_500, width=12
            ),
            _cloudwatch.GraphWidget(
                title='Task running count', left=task_count, width=24
            ),
            _cloudwatch.GraphWidget(
                title='CPU used/reserved %', left=cpu, width=24
            ),
            _cloudwatch.GraphWidget(
                title='Memory used/reserved %', left=memory, width=24
            ),
        )
