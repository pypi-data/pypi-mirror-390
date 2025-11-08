import logging
from collections import Counter
from typing import Dict, List, Optional, Tuple, Union

import marshmallow_dataclass
from ruamel import yaml

from ptal_api.core.type_mapper.data_model.custom_data_model import CustomTypeCodeStorage


class CustomDataHandler:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    @staticmethod
    def unite_all_concept_link_mapping(
        custom_concept_link_type_codes: Dict[str, List[Tuple[str, str, str]]]
    ) -> Dict[Tuple[str, str, str], str]:
        return {
            (key, item[0], item[1]): item[2] for key, value in custom_concept_link_type_codes.items() for item in value
        }

    def get_custom_name_code_mapping(self, file_path: str) -> CustomTypeCodeStorage:
        with open(file_path, encoding="utf-8") as file:
            name_code_mapping = yaml.safe_load(file)
            if name_code_mapping:
                self._verify_custom_name_code_mapping(name_code_mapping)
                return marshmallow_dataclass.class_schema(CustomTypeCodeStorage)().load(name_code_mapping)
            return CustomTypeCodeStorage()

    def _verify_custom_name_code_mapping(
        self, name_code_mapping: Dict[str, Optional[Dict[str, Union[str, List[Tuple[str, str, str]]]]]]
    ) -> None:
        has_duplicate_codes = False
        for object_type, object_mapping in name_code_mapping.items():
            if not object_mapping:
                continue
            if object_type == "concept_link_type_codes":
                mod_object_mapping = self.unite_all_concept_link_mapping(object_mapping)
            else:
                mod_object_mapping = object_mapping
            most_common_code, most_common_count = Counter(mod_object_mapping.values()).most_common(n=1)[0]
            if most_common_count > 1:
                self._logger.error(
                    f'The key "{object_type}" in custom name-code mapping has {most_common_count}'
                    f' type codes named "{most_common_code}". Use unique type codes'
                )
                has_duplicate_codes = True
        if has_duplicate_codes:
            raise Exception("Invalid custom name-code mapping")
