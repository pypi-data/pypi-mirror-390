import logging
from typing import Optional, Union

import marshmallow_dataclass

from ptal_api.core.type_mapper.data_model.base_data_model import TypeMapping
from ptal_api.core.type_mapper.modules.type_mapping_loader.type_mapping_loader_interface import (
    TypeMappingLoaderInterface,
)


class TypeMappingLoader(TypeMappingLoaderInterface):
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)

    def _load_type_mapping_from_file(self, file_path: str) -> Optional[TypeMapping]:
        try:
            with open(file_path, encoding="utf-8") as file:
                type_mapping = marshmallow_dataclass.class_schema(TypeMapping)().loads(file.read())
                self._logger.info(f'Loaded type mapping from file "{file_path}"')
                return type_mapping
        except Exception as ex:
            self._logger.info(f'Failed to load type mapping from file "{file_path}"')
            raise ex

    def _load_type_mapping_from_dict(self, input_dict: dict) -> Optional[TypeMapping]:
        try:
            type_mapping = marshmallow_dataclass.class_schema(TypeMapping)().load(input_dict)
            self._logger.info("Loaded type mapping from input dictionary")
            return type_mapping
        except Exception as ex:
            self._logger.info("Failed to load type mapping from input dictionary")
            raise ex

    def load_type_mapping(self, input_data: Optional[Union[str, dict, TypeMapping]]) -> TypeMapping:
        if isinstance(input_data, TypeMapping):
            return input_data
        if isinstance(input_data, str):
            return self._load_type_mapping_from_file(input_data)
        if isinstance(input_data, dict):
            return self._load_type_mapping_from_dict(input_data)
        return TypeMapping()
