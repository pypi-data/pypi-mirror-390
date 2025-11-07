import builtins
import typing
import aws_cdk
import constructs

from aws_cdk import aws_iam

from aws_cdk_constructs.bucket.base_edge_constructs import BaseEdgeConstruct


class EdgeRole(BaseEdgeConstruct):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_name: str,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param role_name: -
        """

        super().__init__(scope, id)

        self.role = aws_iam.Role(
            self.edge_stack,
            id,
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal('edgelambda.amazonaws.com'),
                aws_iam.ServicePrincipal('lambda.amazonaws.com'),
            ),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    'service-role/AWSLambdaBasicExecutionRole'
                )
            ],
            role_name=role_name,
        )

    def add_to_edge_role_policy(
        self,
        statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> None:
        """
        :param statement: -
        """
        self.role.add_to_policy(statement)
