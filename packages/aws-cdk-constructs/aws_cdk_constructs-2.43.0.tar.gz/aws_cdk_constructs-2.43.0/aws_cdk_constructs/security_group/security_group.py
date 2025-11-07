from ..utils import normalize_environment_parameter

from aws_cdk import (
    aws_ec2 as _ec2,
    Tags,
)

from constructs import Construct


class SecurityGroup(Construct):
    """
    The FAO CDK SecurityGroup Construct creates AWS security grup resources.

    The construct automatically enables the following main features:

    -	Creates an AWS security group;
    -	Enable access from every private FAO client, like FAO HQ and field offices, Pulse secure, etc.

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org


    Args:
        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliance. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        security_group_name (str): The security group name

        vpc (_ec2.IVpc): The VPC in which the load balancer will be created

        allow_all_outbound (str): if the security group should enable outgoing traffic. Default=True

        omit_cloudformation_template_outputs(bool): Omit the generation of CloudFormation template outputs. Default: false

    Returns:
        aws_fao_constructs.security_group.SecurityGroup: the Security group FAO construct that aggregates
        aws_ec2.SecurityGroup: the newly created security group
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name: str,
        environment: str,
        environments_parameters: dict,
        security_group_name: str,
        vpc: _ec2.IVpc,
        allow_all_outbound: bool = True,
        omit_cloudformation_template_outputs: bool = False,
    ) -> None:

        super().__init__(scope, id + '-fao-construct')

        self.environment = normalize_environment_parameter(environment)
        self.environments_parameters = environments_parameters
        self.sg = _ec2.SecurityGroup(
            scope,
            id,
            vpc=vpc,
            security_group_name=security_group_name,
            allow_all_outbound=allow_all_outbound,
        )

        # Apply mandatory tags
        Tags.of(self.sg).add('ApplicationName', app_name.lower().strip())
        Tags.of(self.sg).add('Environment', environment)

    def enable_fao_private_access(self, port: _ec2.Port.tcp) -> None:
        """Apply the correct ingress rules to the provided security group to enable access from the FAO internal networks

        Args:
            port (aws_ec2.Port.tcp): the port to allow, if None tcp_connection_traffic_port will be used

        """

        fao_networks = self.environments_parameters['networking']

        self.sg.add_ingress_rule(
            peer=_ec2.Peer.prefix_list(
                fao_networks['prefixlists_fao_clients']
            ),
            connection=port,
            description='Prefix list FAO Clients',
        )
