from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct

import cdk.demo_service_rest_backend.constants as constants
from cdk.demo_service_rest_backend.monitoring import CrudMonitoring


class ApiConstruct(Construct):

    def __init__(self, scope: Construct, id_: str,
                 appconfig_app_name: str) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.lambda_role = self._build_lambda_role()
        self.common_layer = self._build_common_layer()
        self.create_address_validation = self._add_lambda_integration(self.lambda_role, appconfig_app_name)
        self.monitoring = CrudMonitoring(self, id_, [self.create_address_validation])

    # def _build_api_gw(self) -> aws_apigateway.RestApi:
    #     rest_api: aws_apigateway.RestApi = aws_apigateway.RestApi(
    #         self,
    #         'service-rest-api',
    #         rest_api_name='Service Rest API',
    #         description='This service handles /api/orders requests',
    #         deploy_options=aws_apigateway.StageOptions(throttling_rate_limit=2, throttling_burst_limit=10),
    #         cloud_watch_role=False,
    #     )

    # CfnOutput(self, id=constants.APIGATEWAY, value=rest_api.url).override_logical_id(constants.APIGATEWAY)
    # return rest_api

    def _build_lambda_role(self) -> iam.Role:
        return iam.Role(
            self,
            constants.SERVICE_ROLE_ARN,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamic_configuration':
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=['appconfig:GetLatestConfiguration', 'appconfig:StartConfigurationSession'],
                            resources=['*'],
                            effect=iam.Effect.ALLOW,
                        )
                    ]),
                'appconfig_full_access':  # Add the appConfig_fullAccess policy
                    iam.PolicyDocument(statements=[iam.PolicyStatement(
                        actions=['appconfig:*'],
                        resources=['*'],
                        effect=iam.Effect.ALLOW,
                    )]),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_common_layer(self) -> PythonLayerVersion:
        return PythonLayerVersion(
            self,
            f'{self.id_}{constants.LAMBDA_LAYER_NAME}',
            entry=constants.COMMON_LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _add_lambda_integration(
        self,
        role: iam.Role,
        appconfig_app_name: str,
    ) -> _lambda.Function:

        appconfig_layer = PythonLayerVersion.from_layer_version_arn(
            self, f'{self.id_}AppConfigLayer', layer_version_arn='arn:aws:lambda:us-east-1:027255383542:layer:AWS-AppConfig-Extension:113')
        lambda_function = _lambda.Function(
            self,
            constants.CREATE_LAMBDA,
            function_name='callExternalRestAPI',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='lambda_function.lambda_handler',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'CONFIGURATION_APP': appconfig_app_name,  # for feature flags
                'CONFIGURATION_ENV': constants.ENVIRONMENT,  # for feature flags
                'CONFIGURATION_NAME': constants.CONFIGURATION_NAME,  # for feature flags
                'CONFIGURATION_MAX_AGE_MINUTES': constants.CONFIGURATION_MAX_AGE_MINUTES,  # for feature flags
                #'REST_API': 'https://apibaseurl/api',  # for env vars example
                'ROLE_ARN': 'arn:partition:service:region:account-id:resource-type:resource-id',  # for env vars example
                'USER_ID': constants.USER_ID
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, appconfig_layer],
            role=role,
            log_retention=RetentionDays.ONE_DAY,
        )
        return lambda_function
