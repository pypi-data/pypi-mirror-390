import logging
from typing import Optional

import marshmallow_dataclass

from ptal_api.core.type_mapper.common.common import generate_file
from ptal_api.core.type_mapper.data_model.base_data_model import TypeMapping
from ptal_api.core.type_mapper.data_model.config_data_model import FileGenerationSettings


class FileGenerator:
    def __init__(self, file_generation_settings: Optional[FileGenerationSettings], logger: logging.Logger):
        self._logger = logger
        self._file_generation_settings = (
            file_generation_settings if file_generation_settings else FileGenerationSettings()
        )

    def generate_file(self, type_mapping: TypeMapping, file_path: str) -> None:
        try:
            json_string = (
                marshmallow_dataclass.class_schema(TypeMapping)(only=self._file_generation_settings.generated_fields)
                .dumps(
                    obj=type_mapping,
                    indent=self._file_generation_settings.indent,
                    sort_keys=self._file_generation_settings.sort_keys,
                    ensure_ascii=False,
                )
                .encode("utf-8")
            )

            generate_file(json_string, file_path)
            self._logger.debug(f"Generated file based on type mapping: {file_path}")
        except Exception as ex:
            self._logger.info(f'Failed to generate a file "{file_path}" based on type mapping')
            self._logger.exception(ex)
