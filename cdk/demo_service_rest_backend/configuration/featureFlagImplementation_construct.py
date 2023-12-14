from pathlib import Path
from aws_cdk import aws_appconfig_alpha as appconfig
#import aws_cdk.aws_appconfig_alpha as appconfig
from aws_cdk import Duration, RemovalPolicy
from constructs import Construct

class ConfigurationStoreFF(Construct):

    def __init__(self, scope: Construct, id_: str, environment: str, service_name: str, configuration_name: str) -> None:
        """
        This construct should be deployed in a different repo and have its own pipeline so updates can be decoupled from
        running the service pipeline and without redeploying the service lambdas.

        Args:
            scope (Construct): The scope in which to define this construct.
            id_ (str): The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be
                        replaced by double dash ``--``.
            environment (str): environment name. Used for loading the corresponding JSON file to upload under
                               'configuration/json/{environment}_configuration.json'
            service_name (str): application name.
            configuration_name (str): configuration name
        """
        super().__init__(scope, id_)

        configuration_str = self._get_and_validate_configuration(environment)
        self.app_name = 'featureFlagImp'
        #f'{id_}{service_name}'
        self.config_app = appconfig.Application(
            self,
            id=self.app_name,
            name=self.app_name,
        )

        self.config_app.apply_removal_policy(RemovalPolicy.DESTROY)

        self.config_env = appconfig.Environment(
            self,
            id= 'development',
            #f'{id_}env',
            application=self.config_app,
            name=environment,
        )

        self.config_env.apply_removal_policy(RemovalPolicy.DESTROY)

        # zero minutes, zero bake, 100 growth all at once
        self.config_dep_strategy = appconfig.DeploymentStrategy(
            self,
            f'{id_}zero',
            rollout_strategy=appconfig.RolloutStrategy.linear(
                growth_factor=100,
                deployment_duration=Duration.minutes(0),
                final_bake_time=Duration.minutes(0),
            ),
        )

        self.config_dep_strategy.apply_removal_policy(RemovalPolicy.DESTROY)

        # Create Feature Flags
        feature_flag_1 = appconfig.HostedConfiguration(
            self, f'{id_}FeatureFlag1',
            application=self.config_app,
            #configuration_profile=self.config_env,
            content='{"FeatureFlag1": true}',
            deployment_strategy=self.config_dep_strategy,
        )

        feature_flag_2 = appconfig.HostedConfiguration(
            self, f'{id_}FeatureFlag2',
            application=self.config_app,
            #configuration_profile=self.config_env,
            content='{"FeatureFlag2": true}',
            deployment_strategy=self.config_dep_strategy,
        )

        # workaround until https://github.com/aws/aws-cdk/issues/26804 is resolved
        feature_flag_1.node.default_child.apply_removal_policy(RemovalPolicy.DESTROY)  # type: ignore
        feature_flag_2.node.default_child.apply_removal_policy(RemovalPolicy.DESTROY)  # type: ignore

    def _get_and_validate_configuration(self, environment: str) -> str:
        current = Path(__file__).parent
        conf_filepath = current / (f'json/{environment}_configuration.json')
        configuration_str = conf_filepath.read_text()
        # validate configuration (check feature flags schema structure if exists)
        return configuration_str
