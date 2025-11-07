import builtins
import os
import typing
import aws_cdk
import constructs


class SecretGenerator(
    constructs.Construct,
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allowed_characters: typing.Optional[builtins.str] = None,
        length: typing.Optional[builtins.int] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param allowed_characters: -
        :param length: -
        """

        super().__init__(scope, id)

        dirname = os.path.dirname(__file__)

        secret_generator = aws_cdk.aws_lambda.SingletonFunction(
            self,
            'Function',
            uuid='cloudcomponents-cdk-cloudfront-authorization-secret-generator',
            runtime=aws_cdk.aws_lambda.Runtime.NODEJS_22_X,
            handler='index.handler',
            code=aws_cdk.aws_lambda.Code.from_asset(
                path=os.path.join(dirname, '../lambdas/secret-generator/')
            ),
        )

        cr = aws_cdk.CustomResource(
            self,
            'CustomResource',
            service_token=secret_generator.function_arn,
            resource_type='Custom::GenerateSecret',
            properties={
                'Length': length or 16,
                'AllowedCharacters': allowed_characters
                or 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~',
            },
        )

        self.secret = cr.ref
