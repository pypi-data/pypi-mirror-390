import builtins
import json
import os

import aws_cdk as cdk

from constructs import Construct

from aws_cdk import aws_lambda, aws_iam

from aws_cdk_constructs.bucket.configuration import EdgeLambdaConfiguration


class WithConfiguration(Construct):
    def __init__(
        self,
        scope: Construct,
        id: builtins.str,
        *,
        configuration: EdgeLambdaConfiguration,
        function: aws_lambda.IFunction,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param configuration: -
        :param function: -
        """

        super().__init__(scope, id)

        dirname = os.path.dirname(__file__)

        resourceType = 'Custom::WithEdgeLambdaConfiguration'

        handler = aws_lambda.SingletonFunction(
            self,
            'MyHandler',
            uuid='cloudcomponents-cdk-lambda-at-edge-pattern-with-my-configuration',
            runtime=aws_lambda.Runtime.NODEJS_22_X,
            code=aws_lambda.Code.from_asset(
                os.path.join(dirname, '../lambdas/with_configuration/')
            ),
            handler='index.handler',
            lambda_purpose=resourceType,
            timeout=cdk.Duration.minutes(5),
        )

        handler.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    'lambda:GetFunction',
                    'lambda:UpdateFunctionCode',
                    'lambda:GetFunctionConfiguration',
                ],
                resources=[function.function_arn, '*'],  # TODO: Remove *
            )
        )

        cr = cdk.CustomResource(
            self,
            'WithEdgeLambdaConfiguration',
            service_token=handler.function_arn,
            resource_type=resourceType,
            properties={
                'Region': 'us-east-1',
                'FunctionName': function.function_name,
                'Configuration': json.dumps(configuration._values),
            },
        )

        self.function_version = aws_lambda.Version.from_version_arn(
            self, 'Version', cr.get_att_string('FunctionArn')
        )
