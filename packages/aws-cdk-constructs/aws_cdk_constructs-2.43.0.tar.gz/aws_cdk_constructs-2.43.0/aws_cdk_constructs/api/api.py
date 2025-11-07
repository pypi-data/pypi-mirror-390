import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_apigateway as _apigateway

from aws_cdk_constructs.utils import (
    normalize_environment_parameter,
    get_version,
)
from typing import Union


class Api(Construct):
    @property
    def api(
        self,
    ) -> _apigateway.SpecRestApi:
        """Returns the API Gateway construct

        Returns:
            _apigateway.SpecRestApi: API Gateway construct
        """
        return self._api

    @property
    def key(
        self,
    ) -> _apigateway.ApiKey:
        """Returns the API Gateway key

        bReturns:
            _apigateway.ApiKey: API Gateway key
        """
        return self._key

    @property
    def usage_plan(
        self,
    ) -> _apigateway.UsagePlan:
        """Returns the API Gateway usage plan associated to the key

        bReturns:
            _apigateway.UsagePlan: Returns the API Gateway usage plan associated to the key
        """
        return self._usage_plan

    """

    The FAO CDK Api Construct creates an AWS Api Gateway REST Api, providing a Swagger JSON file.

    Every resource created by the construct will be tagged according to the FAO AWS tagging strategy described at https://aws.fao.org

    Args:

        id (str): the logical id of the newly created resource

        app_name (str): The application name. This will be used to generate the 'ApplicationName' tag for CSI compliancy. The ID of the application. This must be unique for each system, as it will be used to calculate the AWS costs of the system

        environment (str): Specify the environment in which you want to deploy you system. Allowed values: Development, QA, Production, SharedServices

        environments_parameters (dict): The dictionary containing the references to CSI AWS environments. This will simplify the environment promotions and enable a parametric development of the infrastructures.

        api_definition_path (str): The path to the OpenAI definition (or compatible) to use to auto-generate Api Gateway

    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        app_name: str,
        environment: str,
        environments_parameters: dict,
        api_definition_path: str,
        quota: Union[_apigateway.QuotaSettings, None] = None,
        throttle: Union[_apigateway.ThrottleSettings, None] = None,
        stage_options: Union[_apigateway.StageOptions, None] = None,
        domain_name_options: Union[_apigateway.DomainNameOptions, None] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        environment = normalize_environment_parameter(environment)

        # Apply mandatory tags
        cdk.Tags.of(self).add('ApplicationName', app_name.lower().strip())
        cdk.Tags.of(self).add('Environment', environment)

        # Apply FAO CDK tags
        cdk.Tags.of(self).add('fao-cdk-construct', 'api')
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk-version', get_version())
        cdk.Tags.of(cdk.Stack.of(self)).add('fao-cdk', 'true')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create conditions
        api_definition_path = api_definition_path.strip()

        environment_lower = environment.lower()
        aws_account = environments_parameters['accounts'][environment_lower]

        self._api = _apigateway.SpecRestApi(
            self,
            f'{id}-{environment_lower}',
            api_definition=_apigateway.ApiDefinition.from_asset(
                api_definition_path
            ),
            domain_name=domain_name_options if domain_name_options else None,
            deploy_options=(
                stage_options
                if stage_options
                else _apigateway.StageOptions(
                    cache_data_encrypted=False,
                    caching_enabled=False,
                    data_trace_enabled=False,
                    description=f'[{app_name}] {id} {environment_lower}',
                    stage_name=environment_lower,
                )
            ),
        )

        self._usage_plan = self._api.add_usage_plan(
            f'{id}-{environment_lower}-usage-plan',
            name=f'{id}-{environment_lower}-usage-plan',
            quota=quota,
            throttle=throttle,
        )

        self._usage_plan.add_api_stage(
            stage=self._api.deployment_stage,
        )

        self._key = self._api.add_api_key(
            f'{id}-{environment_lower}-key',
            api_key_name=f'{id}-{environment_lower}-key',
        )
        self._usage_plan.add_api_key(self._key)
