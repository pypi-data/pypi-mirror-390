import builtins
import typing
from datetime import datetime
import typing_extensions
import aws_cdk


from constructs import Construct

from aws_cdk import (
    aws_lambda,
    aws_cloudfront,
    aws_ssm,
    custom_resources,
)

from aws_cdk_constructs.bucket.configuration import EdgeLambdaConfiguration
from aws_cdk_constructs.bucket.edge_role import EdgeRole
from aws_cdk_constructs.bucket.base_edge_constructs import BaseEdgeConstruct
from aws_cdk_constructs.bucket.with_configuration import WithConfiguration


class EdgeFunctionProvider(Construct):
    def __init__(
        self,
        scope: Construct,
        id: builtins.str,
        *,
        parameter: aws_ssm.IStringParameter,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param parameter: -
        """

        super().__init__(scope, id)

        cr = custom_resources.AwsCustomResource(
            self,
            'Resource',
            on_update={
                'service': 'SSM',
                'action': 'getParameter',
                'parameters': {
                    'Name': parameter.parameter_name,
                },
                'region': 'us-east-1',
                'physical_resource_id': custom_resources.PhysicalResourceId.of(
                    str(datetime.now().microsecond)
                ),
            },
            install_latest_aws_sdk=False,
            policy=custom_resources.AwsCustomResourcePolicy.from_sdk_calls(
                resources=[parameter.parameter_arn],
            ),
        )

        self.edge_function = aws_lambda.Function.from_function_arn(
            self, 'Function', cr.get_response_field('Parameter.Value')
        )


class EdgeFunction(BaseEdgeConstruct):
    def __init__(
        self,
        scope: Construct,
        id: builtins.str,
        *,
        code: aws_lambda.Code,
        configuration: EdgeLambdaConfiguration,
        event_type: aws_cloudfront.LambdaEdgeEventType,
        name: builtins.str,
        edge_role=None,
        parameter_name=None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param code: -
        :param configuration: -
        :param event_type: -
        :param name: -
        :param edge_role: -
        :param parameter_name: The name of the parameter.
        """

        super().__init__(scope, id)

        stack = (
            self._stack
            if self._stack.nested_stack_parent is None
            else self._stack.nested_stack_parent
        )

        parameter_name = (
            '/cloudcomponents/cloudfront-lambda/'
            + stack.stack_name
            + '/'
            + name
            + '/'
            + self._stack.node.addr
        )

        role = (
            EdgeRole(self, name + 'Role') if edge_role is None else edge_role
        )

        self._edge_role = role

        self._event_type = event_type

        edge_function = aws_lambda.Function(
            self._edge_stack,
            name + 'Function',
            runtime=aws_lambda.Runtime.NODEJS_22_X,
            handler='index.handler',
            code=code,
            role=role.role,
        )

        parameter = aws_ssm.StringParameter(
            self._edge_stack,
            name + 'StringParameter',
            parameter_name=parameter_name,
            description='Parameter stored for cross region Lambda@Edge',
            string_value=edge_function.function_arn,
        )

        edgeFunctionProvider = EdgeFunctionProvider(
            scope, name + 'Provider', parameter=parameter
        )
        retrievedEdgeFunction = edgeFunctionProvider.edge_function

        lambdaWithConfig = WithConfiguration(
            self,
            'WithConfiguration',
            function=retrievedEdgeFunction,
            configuration=configuration,
        )

        self._function_version = lambdaWithConfig.function_version

        self._edge_lambda = aws_cdk.aws_cloudfront.EdgeLambda(
            function_version=self._function_version,
            event_type=self._event_type,
        )

    @property
    def edge_lambda(self):
        return self._edge_lambda
