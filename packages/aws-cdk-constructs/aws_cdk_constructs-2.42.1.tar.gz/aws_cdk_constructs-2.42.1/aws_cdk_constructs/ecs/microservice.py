from __future__ import annotations

import os
from typing import Optional, List, Dict, TYPE_CHECKING

from aws_cdk import (
    Tags,
    Duration,
    Size,
    aws_ec2 as _ec2,
    aws_ecs as _ecs,
    aws_ecr as _ecr,
    aws_logs as _logs,
    aws_ecr_assets as _ecr_assets,
    aws_elasticloadbalancingv2 as _elb,
    aws_route53 as _route53,
    aws_cloudwatch as _cloudwatch,
)
from constructs import Construct

from aws_cdk_constructs.ecs.fargate_validator import FargateValidator
from aws_cdk_constructs.efs.volume import EFSVolume

if TYPE_CHECKING:
    from .cluster import ECSCluster


class ECSMicroservice(Construct):
    """

    The FAO CDK ECSMicroservice Construct represents a microservice in a CDK ECSCluster; this class aggregates all AWS entities that will become a FargateService and TaskDefinition.

    The construct automatically enables the following main features:

    -	FargateService and TaskDefinition creation, with container image and tag definition, CPU, memory setup, memory limit and CPU limit, entry point, port, health check path, desired count, max and min number of containers, and more;
    -	Docker image definition from AWS Elastic Registry Service (AWS ECR) or as a local asset;
    -	Auto Scaling and Self-Healing configuration;
    -	Native integration with FAO CDK Load Balancer construct and multiple registrations of microservices as targets of the AWS Application Load Balancer;
    -	Native integration with FAO CDK EFS construct to create AWS EFS volumes and attach them to containers;
    -	Native integration with the FAO Instance Scheduler to automatically control the uptime of the ECS tasks;
    -	Private DNS record creation for non-Production environments;
    -	Enable access to the FAO SMTP servers if the microservices need to send email notifications (additional configuration at the container level may be required);
    -	Conditionally tracking of ECS task metrics in the FAO CloudWatch dashboard;

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:
        scope (Construct): Parent construct

        name (str): logical id of the new created service

        image (Optional|str): ECR docker image, it must be uploaded to the account ECR registry

        dockerfile_path (Optional|str): ECR Dockerfile directory path

        cluster (ECSCluster): ECSCluster entity where the microservice will be deployed.

        image_tag (str): tag of the ECR hosted docker image, defaults to "master".

        container_env (Dict): A dictionary that will be injected on the running containers as environment variables.

        cpu (int): Number of CPU units to be allocated to the container, see (https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateTaskDefinition.html#cpu) for valid cpu/mem values combination.

        memory_limit_mib (int): The hard limit (in MiB) of memory to present to the container, see (https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateTaskDefinition.html#memorylimitmib) for valid cpu/mem values combination.

        entry_point (List): The entry point that is passed to the container, see (https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ContainerDefinition.html#entrypoint) for more details.

        port (int): The port number on the container that is bound to the user-specified or automatically assigned host port.

        health_check_path (str): The path to the container health check, defaults to "/".

        desired_count (int): The number of instances of the task definition to place and keep running, defaults to 1.

        max_count (int): The maximum number of instances of the task definition to place and keep running, defaults to None.

        min_count (int): The minimum number of instances of the task definition to place and keep running, defaults to 1.

        cpu_threshold (int): The target value for the average CPU utilization across an application, defaults to 50.

        security_group (aws_ec2.SecurityGroup): Security group to attach to the service, if None a dedicated SG will be created.

        sends_emails (bool): If the service sends emails, defaults to False.

        tag_scheduler_uptime (str): specifies the time range in which the AWS resource should be kept up and running - format `HH:mm-HH:mm` (i.e. 'start'-'end'), where the 'start' time must be before 'end'

        tag_scheduler_uptime_days (str): weekdays in which the `SchedulerUptime` tag should be enforced. If not specified, `SchedulerUptime` will be enforced during each day of the week - format integer from 1 to 7, where 1 is Monday

        tag_scheduler_uptime_skip (str): to skip optimization check - format Boolean (`true`, `false`)

        healthy_threshold_count (int): The number of consecutive health checks successes required before considering an unhealthy target healthy, defaults to 2.

        unhealthy_threshold_count (int): The number of consecutive health check failures required before considering the target unhealthy, defaults to 2.

        health_check_interval (int): The approximate amount of time, in seconds, between health checks of an individual target, defaults to 30.

        health_check_timeout (int): The amount of time, in seconds, during which no response means a failed health check, defaults to 5.

        internal (bool): When set to true the ms won't be registered in the Alb target group

        alternative_fqdns (List[str]): List of alternative FQDNs to register in the Alb target group

        omit_cloudformation_template_outputs(bool): Omit the generation of CloudFormation template outputs. Default: false

        log_driver_blocking_mode (bool): Whet set to true if the logs destination stops working, the application will be blocked. When set to False, the logs will be lost but the application keeps working. Default: false

        max_buffer_size_mib (int): The size (mebibytes) of the buffer when log_driver_blocking_mode is set to false. Default: 4

        deploy_to_ec2 (bool): When set to true the service will be deployed to EC2 instead of Fargate. Default: false

    """

    def __init__(
        self,
        scope: Construct,
        name: str,
        cluster: ECSCluster,
        dockerfile_path: str = None,
        image: str = None,
        image_tag: str = 'master',
        container_env: dict = None,
        cpu: int = 256,
        memory_limit_mib: int = 512,
        entry_point: list = None,
        port: int = 80,
        health_check_path: str = '/',
        desired_count: int = 1,
        max_count: int = None,
        min_count: int = None,
        cpu_threshold: int = None,
        security_group: _ec2.SecurityGroup = None,
        sends_emails: bool = False,
        tag_scheduler_uptime: str = '08:00-18:00',
        tag_scheduler_uptime_days: str = '1-2-3-4-5',
        tag_scheduler_uptime_skip: str = 'false',
        healthy_threshold_count: int = 2,
        unhealthy_threshold_count: int = 2,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        internal: bool = False,
        alternative_fqdns: list[str] = [],
        ephemeral_storage_gib: int = 21,
        omit_cloudformation_template_outputs: bool = False,
        log_driver_blocking_mode: bool = False,
        max_buffer_size_mib: int = 4,
        deploy_to_ec2: [bool] = False,
    ) -> None:
        self.scope = scope
        self.id = name
        self.dockerfile_path = dockerfile_path
        self.image = image
        self.image_tag = image_tag
        self.container_env = container_env
        self.cpu = cpu
        self.memory_limit_mib = memory_limit_mib
        self.entry_point = entry_point
        self.vpc = cluster.vpc
        self.cluster = cluster
        self.port = port
        self.health_check_path = health_check_path
        self.hostname = (
            f'{self.id}-{self.cluster.app_name}.{self.cluster.domain_name}'
        )
        self.cname: Optional[_route53.CnameRecord] = None
        self.desired_count = desired_count
        self.max_count = max_count
        self.min_count = min_count
        self.cpu_threshold = cpu_threshold
        self.environments_parameters = self.cluster.environments_parameters
        self.environment = self.cluster.environment
        self.log_driver_blocking_mode = log_driver_blocking_mode
        self.max_buffer_size_mib = max_buffer_size_mib
        self.ephemeral_storage_gib = ephemeral_storage_gib
        self.deploy_to_ec2 = deploy_to_ec2

        if not log_driver_blocking_mode:
            # Configure ECS logging in non-blocking mode and the buffer size when the log_driver_blocking_mode is set to False (default value)
            self.log_driver_mode = _ecs.AwsLogDriverMode.NON_BLOCKING
            self.max_buffer_size = Size.mebibytes(self.max_buffer_size_mib)
        else:
            # Configure ECS logging in blocking mode and remove the buffer when the log_driver_blocking_mode is set to True
            self.log_driver_mode = _ecs.AwsLogDriverMode.BLOCKING
            self.max_buffer_size = None

        super().__init__(scope, name)
        FargateValidator(cpu=self.cpu, mem=self.memory_limit_mib)

        # Create a dedicated SG if none is provided
        self.security_groups: List[_ec2.ISecurityGroup] = []
        if not security_group:
            self.security_group = self._create_sg()
        else:
            self.security_group = security_group

        self.security_groups.append(self.security_group)

        # Requirement to send emails is to have the SMTP SG attached to the service

        if sends_emails:
            smtp_relay_sg_id = self.cluster.aws_account.get(
                'smtp_relay_security_group'
            )
            smtp_relay_sg = _ec2.SecurityGroup.from_security_group_id(
                scope=scope,
                id=f'{self.id}_smtp-access-sg',
                security_group_id=smtp_relay_sg_id,
                mutable=False,
            )
            self.security_groups.append(smtp_relay_sg)

        self.task = self._create_task()
        self.main_container = self._create_main_container()
        self.service = self._create_service()

        # It will attach services to the LB listener and route them by hostname
        if self.cluster.alb is not None and internal is False:
            lb_target_priority = self.cluster.alb.get_safe_rule_priority()
            self.cluster.target_priority = lb_target_priority

            if self.deploy_to_ec2:
                self.target_group = self.cluster.alb.listener.add_targets(
                    self.id,
                    targets=[self.service],
                    priority=lb_target_priority,
                    protocol=_elb.ApplicationProtocol.HTTP,
                    health_check=_elb.HealthCheck(
                        path=self.health_check_path,
                        healthy_threshold_count=healthy_threshold_count,
                        unhealthy_threshold_count=unhealthy_threshold_count,
                        interval=Duration.seconds(health_check_interval),
                        timeout=Duration.seconds(health_check_timeout),
                    ),
                    conditions=[
                        _elb.ListenerCondition.host_headers(
                            [
                                f'{self.id}-{self.cluster.app_name}.{self.cluster.domain_name}'
                            ]
                        )
                    ],
                )
            else:
                self.target_group = self.cluster.alb.listener.add_targets(
                    self.id,
                    port=self.port,
                    targets=[self.service],
                    priority=lb_target_priority,
                    protocol=_elb.ApplicationProtocol.HTTP,
                    health_check=_elb.HealthCheck(
                        port=str(self.port),
                        path=self.health_check_path,
                        healthy_threshold_count=healthy_threshold_count,
                        unhealthy_threshold_count=unhealthy_threshold_count,
                        interval=Duration.seconds(health_check_interval),
                        timeout=Duration.seconds(health_check_timeout),
                    ),
                    conditions=[
                        _elb.ListenerCondition.host_headers(
                            [
                                f'{self.id}-{self.cluster.app_name}.{self.cluster.domain_name}'
                            ]
                        )
                    ],
                )
            if alternative_fqdns:
                for fqdn in alternative_fqdns:
                    lb_target_priority = (
                        self.cluster.alb.get_safe_rule_priority()
                    )
                    self.cluster.target_priority = lb_target_priority
                    self.cluster.alb.listener.add_action(
                        f'{self.id}-action-{lb_target_priority}',
                        action=_elb.ListenerAction.forward(
                            target_groups=[self.target_group]
                        ),
                        priority=lb_target_priority,
                        conditions=[
                            _elb.ListenerCondition.host_headers([fqdn])
                        ],
                    )

            if deploy_to_ec2:
                self.cluster.alb.security_group.add_ingress_rule(
                    peer=self.cluster.ecs_sg,
                    connection=_ec2.Port.all_traffic(),
                    description='Allow ALB to access the service',
                )
            else:

                self.cluster.alb.security_group.add_ingress_rule(
                    peer=self.security_group,
                    connection=_ec2.Port.all_traffic(),
                    description='Allow ALB to access the service',
                )

        if self.cluster.hosted_zone:
            self.create_cname(self.cluster.hosted_zone)

        if self.max_count and self.min_count and self.cpu_threshold:
            self.scalable_target = self._create_autoscaling()
            if self.scalable_target:
                self.scalable_target.scale_on_cpu_utilization(
                    'CpuScaling', target_utilization_percent=self.cpu_threshold
                )

        self.create_desired_count_tag()
        if self.min_count:
            self.create_min_count_tag()
        self.create_scheduler_tag(
            tag_scheduler_uptime,
            tag_scheduler_uptime_days,
            tag_scheduler_uptime_skip,
        )

        cluster.register_ms(self)

    def _create_sg(self) -> _ec2.SecurityGroup:
        """Default SG creation for the service"""
        return _ec2.SecurityGroup(
            scope=self.scope,
            id=self.id + '-sg',
            vpc=self.vpc,
            allow_all_outbound=True,
        )

    def _create_task(self) -> _ecs.FargateTaskDefinition:
        """Create the task definition

        :returns: aws_ecs.FargateTaskDefinition object
        """
        if self.deploy_to_ec2:
            task = _ecs.TaskDefinition(
                compatibility=_ecs.Compatibility.EC2,
                scope=self.scope,
                id=self.id + '-task',
            )
            return task
        else:

            return _ecs.FargateTaskDefinition(
                scope=self.scope,
                id=self.id + '-task',
                cpu=self.cpu,
                memory_limit_mib=self.memory_limit_mib,
                ephemeral_storage_gib=self.ephemeral_storage_gib,
            )

    def _create_main_container(self) -> _ecs.ContainerDefinition:
        """Create the main container for the service,  based on the ECR image and attaches it to the task definition

        :returns: aws_ecs.ContainerDefinition object
        """
        if self.image:
            image = _ecs.ContainerImage.from_ecr_repository(
                _ecr.Repository.from_repository_name(
                    scope=self.scope,
                    id=self.id + '-ecr-repo',
                    repository_name=self.image,
                ),
                self.image_tag,
            )
        else:
            image = _ecs.ContainerImage.from_docker_image_asset(
                _ecr_assets.DockerImageAsset(
                    self,
                    f'{self.id}-main-image',
                    directory=self.dockerfile_path,
                )
            )

        if self.deploy_to_ec2:
            return self.task.add_container(
                id=self.id + '-main-container',
                image=image,
                cpu=self.cpu,
                memory_reservation_mib=self.memory_limit_mib,
                port_mappings=[_ecs.PortMapping(container_port=self.port)],
                logging=_ecs.LogDriver.aws_logs(
                    stream_prefix=self.id + '-main-container',
                    log_retention=_logs.RetentionDays.ONE_WEEK,
                    mode=self.log_driver_mode,
                    max_buffer_size=self.max_buffer_size,
                ),
                environment=self.container_env,
                entry_point=self.entry_point,
            )
        else:
            return self.task.add_container(
                id=self.id + '-main-container',
                image=image,
                port_mappings=[_ecs.PortMapping(container_port=self.port)],
                logging=_ecs.LogDriver.aws_logs(
                    stream_prefix=self.id + '-main-container',
                    log_retention=_logs.RetentionDays.ONE_WEEK,
                    mode=self.log_driver_mode,
                    max_buffer_size=self.max_buffer_size,
                ),
                environment=self.container_env,
                entry_point=self.entry_point,
            )

    def _create_autoscaling(self) -> Optional[_ecs.ScalableTaskCount]:
        """Create the autoscaling settings for the service, if there's a max_number of replicas"""
        if self.max_count:
            return self.service.auto_scale_task_count(
                min_capacity=self.min_count,
                max_capacity=self.max_count,
            )
        return None

    def _create_service(self) -> _ecs.FargateService:
        """Creates the Fargate Service"""
        if self.deploy_to_ec2:
            return _ecs.Ec2Service(
                scope=self.scope,
                id=self.id + '-srv',
                task_definition=self.task,
                cluster=self.cluster.cluster,
                enable_execute_command=False,
                desired_count=self.desired_count,
                propagate_tags=_ecs.PropagatedTagSource.SERVICE,
            )
        else:
            return _ecs.FargateService(
                scope=self.scope,
                id=self.id + '-srv',
                task_definition=self.task,
                security_groups=self.security_groups,
                cluster=self.cluster.cluster,
                enable_execute_command=True,
                desired_count=self.desired_count,
                propagate_tags=_ecs.PropagatedTagSource.SERVICE,
            )

    def attach_volume(self, name: str, mount_point: str) -> EFSVolume:
        """Public method to create and attach an EFS volume to the containers

        :param name: Name of the volume
        :param mount_point: Mount point of the volume
        :returns: EFSVolume object
        """
        volume = EFSVolume(
            self.scope,
            id=name,
            vpc=self.vpc,
            volume_mount_path=mount_point,
            environment=self.environment,
            environments_parameters=self.environments_parameters,
            app_name=self.cluster.app_name,
        )
        if self.deploy_to_ec2:
            volume.grant_access(self.cluster.ecs_sg)
        else:
            volume.grant_access(self.security_group)

        self.task.node.add_dependency(volume)
        self.task.add_volume(
            name=volume.id,
            efs_volume_configuration=volume.efs_volume_configuration,
        )
        self.main_container.add_mount_points(volume.get_mount_point())
        return volume

    def add_init_container(
        self, name: str, volume: EFSVolume, dockerfile_path: str
    ) -> None:
        """Public method to add an init container to the service, init container will be created based on a Dockerfile
        present on the provided path, it can have a Volume attached to populate init values before attaching it to the main
        container. There's a dependency between the init container and the main container, so the later one will not start
        until the init finished successfully

        :param name: Name of the init container
        :param volume: EFSVolume object to attach to the init container
        :param dockerfile_path: Path to the Dockerfile to build the init container
        """
        init_container_image = _ecr_assets.DockerImageAsset(
            scope=self.scope,
            id=f'{self.id}-{self.id}-{name}-icontainer-image',
            directory=os.getcwd() + dockerfile_path,
        )

        if self.deploy_to_ec2:
            init_container = self.task.add_container(
                id=f'{self.id}-{name}-init-container',
                image=_ecs.ContainerImage.from_docker_image_asset(
                    init_container_image
                ),
                cpu=self.cpu,
                memory_reservation_mib=self.memory_limit_mib,
                essential=False,
                logging=_ecs.LogDriver.aws_logs(
                    stream_prefix=f'{self.id}-{name}-init-container',
                    log_retention=_logs.RetentionDays.ONE_WEEK,
                    mode=self.log_driver_mode,
                    max_buffer_size=self.max_buffer_size,
                ),
            )
        else:

            init_container = self.task.add_container(
                id=f'{self.id}-{name}-init-container',
                image=_ecs.ContainerImage.from_docker_image_asset(
                    init_container_image
                ),
                essential=False,
                logging=_ecs.LogDriver.aws_logs(
                    stream_prefix=f'{self.id}-{name}-init-container',
                    log_retention=_logs.RetentionDays.ONE_WEEK,
                    mode=self.log_driver_mode,
                    max_buffer_size=self.max_buffer_size,
                ),
            )

        init_container.node.add_dependency(volume)
        self.main_container.add_container_dependencies(
            _ecs.ContainerDependency(
                container=init_container,
                condition=_ecs.ContainerDependencyCondition.SUCCESS,
            )
        )
        init_container_mount_point = _ecs.MountPoint(
            read_only=False, container_path='/dst_dir', source_volume=volume.id
        )
        init_container.add_mount_points(init_container_mount_point)

    def create_cname(self, zone: _route53.IHostedZone) -> None:
        """Public method to create a CNAME record for the service, it will have the format <service_name>.<domain_name>
        and it will point to the lb address
        :param zone: Route53 Hosted Zone object
        """
        self.cname = _route53.CnameRecord(
            scope=self.scope,
            id=f'{self.id}-cname',
            zone=zone,
            record_name=f'{self.id}-{self.cluster.app_name}',
            domain_name=f'{self.cluster.alb.alb.load_balancer_dns_name}',
        )

    def create_desired_count_tag(self) -> None:
        """Public method to create the desired count tag for the service"""
        Tags.of(self.service).add(
            key='SchedulerDesiredCount', value=str(self.desired_count)
        )

    def create_min_count_tag(self) -> None:
        """Public method to create the min count tag in case of autoscaling"""
        Tags.of(self.service).add(
            key='SchedulerDesiredCount', value=str(self.min_count)
        )

    def create_scheduler_tag(
        self,
        tag_scheduler_uptime: str,
        tag_scheduler_uptime_days: str,
        tag_scheduler_uptime_skip: str,
    ) -> None:
        Tags.of(self.service).add(
            key='SchedulerUptime', value=tag_scheduler_uptime
        )
        Tags.of(self.service).add(
            key='SchedulerUptimeDays', value=tag_scheduler_uptime_days
        )
        Tags.of(self.service).add(
            key='SchedulerSkip', value=tag_scheduler_uptime_skip
        )

    def create_widgets(self) -> None:
        running_container_count = _cloudwatch.Metric(
            metric_name='RunningTaskCount',
            namespace='ECS/ContainerInsights',
            dimensions_map={
                'ClusterName': self.cluster.cluster.cluster_name,
                'ServiceName': self.service.service_name,
            },
            period=Duration.minutes(5),
            statistic='Average',
        )

        desired_container_count = _cloudwatch.Metric(
            metric_name='DesiredTaskCount',
            color='#98df8a',
            namespace='ECS/ContainerInsights',
            dimensions_map={
                'ClusterName': self.cluster.cluster.cluster_name,
                'ServiceName': self.service.service_name,
            },
            period=Duration.minutes(5),
            statistic='Average',
        )

        left_annotations = (
            [
                _cloudwatch.HorizontalAnnotation(
                    label='Min count', value=self.min_count, color='#98df8a'
                ),
                _cloudwatch.HorizontalAnnotation(
                    label='Max count', value=self.max_count, color='#ff9896'
                ),
            ]
            if (self.min_count and self.max_count)
            else []
        )
        if self.cluster.dashboard:
            self.cluster.dashboard.add_widgets(
                _cloudwatch.GraphWidget(
                    title=f'{self.id} - CPU',
                    left=[
                        _cloudwatch.Metric(
                            metric_name='CpuUtilized',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster.cluster_name,
                                'ServiceName': self.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                        ),
                        _cloudwatch.Metric(
                            metric_name='CpuReserved',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster.cluster_name,
                                'ServiceName': self.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                        ),
                    ],
                ),
                _cloudwatch.GraphWidget(
                    title=f'{self.id} - Memory',
                    left=[
                        _cloudwatch.Metric(
                            metric_name='MemoryUtilized',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster.cluster_name,
                                'ServiceName': self.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                        ),
                        _cloudwatch.Metric(
                            metric_name='MemoryReserved',
                            namespace='ECS/ContainerInsights',
                            dimensions_map={
                                'ClusterName': self.cluster.cluster.cluster_name,
                                'ServiceName': self.service.service_name,
                            },
                            period=Duration.minutes(5),
                            statistic='Average',
                        ),
                    ],
                ),
                _cloudwatch.GraphWidget(
                    title=f'{self.id} - Running containers',
                    left=[running_container_count, desired_container_count],
                    left_annotations=left_annotations,
                ),
            )
