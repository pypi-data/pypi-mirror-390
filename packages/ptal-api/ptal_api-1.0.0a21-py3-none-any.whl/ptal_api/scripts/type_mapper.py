import logging.config
import os
from typing import Optional

import click

from ptal_api.core.type_mapper.data_model.base_data_model import TypeMapping

current_directory_name = os.path.dirname(__file__)
logging.config.fileConfig(
    f"{current_directory_name if current_directory_name else '.'}/../core/type_mapper/app_settings/logging.conf",
    disable_existing_loggers=False,
)
logger = logging.getLogger("type_mapper")

graphql_uri = os.environ.get("GRAPHQL_URI", None)
keykloak_auth_url = os.environ.get("KEYCLOAK_AUTH_URL", None)
realm = os.environ.get("KEYCLOAK_REALM", None)
cliend_id = os.environ.get("KEYCLOAK_CLIENT_ID", None)
client_key = os.environ.get("KEYCLOAK_CLIENT_KEY", None)
user = os.environ.get("KEYCLOAK_USER", None)
pwd = os.environ.get("KEYCLOAK_PWD", None)


@click.command()
@click.option(
    "--file_path",
    required=False,
    type=str,
    default=None,
    help="The path to the file to be generated."
    '\n\nExample: "./files/file_name.json". The default value is "./type_mapping/type_mapping.json".',
)
@click.option(
    "--custom_name_code_mapping_file_path",
    required=False,
    type=str,
    default=None,
    help="The path to the custom name-code mapping file." '\n\nExample: "./model_parameters/name_code_mapping.yml".',
)
def generate_type_mapping_file(
    file_path: Optional[str], custom_name_code_mapping_file_path: Optional[str]
) -> TypeMapping:
    from ptal_api.core.type_mapper.data_model.config_data_model import DefaultTypeCodeStorage, FileGenerationSettings
    from ptal_api.core.type_mapper.modules.custom_data_handler import CustomDataHandler
    from ptal_api.core.type_mapper.modules.file_generator import FileGenerator
    from ptal_api.core.type_mapper.modules.type_mapping_generator import TypeMappingGenerator

    api_adapter = _generate_api_adapter()
    file_generation_settings = FileGenerationSettings()
    file_path = file_path if file_path else file_generation_settings.default_file_path

    default_type_code_storage = DefaultTypeCodeStorage()

    custom_type_code_storage = None
    if custom_name_code_mapping_file_path:
        custom_data_handler = CustomDataHandler(logger)
        custom_type_code_storage = custom_data_handler.get_custom_name_code_mapping(custom_name_code_mapping_file_path)
        logger.info(
            f'The custom name-code mapping file "{custom_name_code_mapping_file_path}"'
            f" has been successfully processed"
        )

    logger.info("The type name-code mapping process has started")
    type_mapping_generator = TypeMappingGenerator(
        api_adapter, logger, default_type_code_storage, custom_type_code_storage
    )
    type_mapping = type_mapping_generator.process_type_mapping()
    logger.info("The type name-code mapping process has completed successfully")

    logger.info("The output file generating process has begun")
    file_generator = FileGenerator(file_generation_settings, logger)
    file_generator.generate_file(type_mapping, file_path)
    logger.info(f"The output file generating process has completed successfully" f"\nThe output file: {file_path}")
    return type_mapping


def _generate_api_adapter():
    from ptal_api.adapter import TalismanAPIAdapter
    from ptal_api.providers.gql_providers import KeycloakAwareGQLClient

    gql_client = KeycloakAwareGQLClient(
        graphql_uri,
        10000,
        5,
        auth_url=keykloak_auth_url,
        realm=realm,
        client_id=cliend_id,
        user=user,
        pwd=pwd,
        client_secret=client_key,
    ).__enter__()
    return TalismanAPIAdapter(gql_client, None)


if __name__ == "__main__":
    generate_type_mapping_file()
