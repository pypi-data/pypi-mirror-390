import builtins
from os import path
import os
import typing
import aws_cdk
import constructs
from aws_cdk_constructs.bucket.edge_role import EdgeRole
from aws_cdk_constructs.bucket.edge_function import EdgeFunction
from aws_cdk_constructs.bucket.configuration import EdgeLambdaConfiguration

from aws_cdk_constructs.bucket.log_level import LogLevel

from aws_cdk import aws_lambda, aws_cloudfront

dirname = os.path.dirname(__file__)


class RedirectPaths(typing.TypedDict):
    sign_in: str
    auth_refresh: str
    sign_out: str


class AuthFlow(constructs.Construct):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_name: str,
        cognito_auth_domain: builtins.str,
        cookie_settings: typing.Mapping[builtins.str, builtins.str],
        log_level: LogLevel,
        nonce_signing_secret: builtins.str,
        oauth_scopes: typing.Sequence[aws_cdk.aws_cognito.OAuthScope],
        redirect_paths: RedirectPaths,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        user_pool_client: aws_cdk.aws_cognito.IUserPoolClient,
        client_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param cognito_auth_domain: -
        :param cookie_settings: -
        :param log_level: -
        :param nonce_signing_secret: -
        :param oauth_scopes: -
        :param redirect_paths: -
        :param user_pool: -
        :param user_pool_client: -
        :param client_secret: -
        """
        super().__init__(scope, id)

        self.edge_role = EdgeRole(self, 'EdgeRole', app_name=app_name)

        self.configuration = EdgeLambdaConfiguration(
            **{
                'logLevel': log_level.value,
                'redirectPathSignIn': redirect_paths.get('sign_in'),
                'redirectPathAuthRefresh': redirect_paths.get('auth_refresh'),
                'redirectPathSignOut': redirect_paths.get('sign_out'),
                'userPoolId': user_pool.user_pool_id,
                'clientId': user_pool_client.user_pool_client_id,
                'oauthScopes': list(
                    map(lambda scope: scope.scope_name, oauth_scopes)
                ),
                'cognitoAuthDomain': cognito_auth_domain,
                'cookieSettings': cookie_settings,
                'nonceSigningSecret': nonce_signing_secret,
                'clientSecret': client_secret,
            }
        )

        self.check_auth = EdgeFunction(
            self,
            'CheckAuth',
            name='check-auth',
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, '../lambdas/check-auth/')
            ),
            edge_role=self.edge_role,
            configuration=self.configuration,
            event_type=aws_cloudfront.LambdaEdgeEventType.VIEWER_REQUEST,
        )

        self.parse_auth = EdgeFunction(
            self,
            'ParseAuth',
            name='parse-auth',
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, '../lambdas/parse-auth/')
            ),
            edge_role=self.edge_role,
            configuration=self.configuration,
            event_type=aws_cloudfront.LambdaEdgeEventType.VIEWER_REQUEST,
        )

        self.refresh_auth = EdgeFunction(
            self,
            'RefreshAuth',
            name='refresh-auth',
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, '../lambdas/refresh-auth/')
            ),
            edge_role=self.edge_role,
            configuration=self.configuration,
            event_type=aws_cloudfront.LambdaEdgeEventType.VIEWER_REQUEST,
        )

        self.sign_out = EdgeFunction(
            self,
            'SignOut',
            name='sign-out',
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, '../lambdas/sign-out/')
            ),
            edge_role=self.edge_role,
            configuration=self.configuration,
            event_type=aws_cloudfront.LambdaEdgeEventType.VIEWER_REQUEST,
        )

    def add_edge_function(
        self, name, path, event_type: aws_cloudfront.LambdaEdgeEventType
    ):
        return EdgeFunction(
            self,
            name,
            name=name,
            code=aws_lambda.Code.from_asset(
                path=os.path.join(dirname, f'../lambdas/{path}')
            ),
            edge_role=self.edge_role,
            configuration=self.configuration,
            event_type=event_type,
        )
