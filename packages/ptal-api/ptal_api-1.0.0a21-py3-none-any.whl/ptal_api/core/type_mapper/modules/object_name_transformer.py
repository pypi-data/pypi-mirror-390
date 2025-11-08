from typing import Dict, Optional, Tuple

from ptal_api.core.type_mapper.common.common import perform_transliteration
from ptal_api.core.type_mapper.data_model.base_data_model import TypeMapping
from ptal_api.core.type_mapper.data_model.custom_data_model import CustomTypeCodeStorage


class ObjectTypeNameTransformer:
    @staticmethod
    def _generate_concept_link_name(
        concept_from_type_name: str, concept_link_type_name: str, concept_to_type_name: str
    ) -> str:
        return f"{concept_from_type_name} {concept_link_type_name} {concept_to_type_name}"

    def create_transformed_object_type_name(
        self,
        object_name: str,
        default_name: str,
        cache_names: Dict[str, str],
        *custom_object_type_code_dicts: Dict[str, str],
    ) -> Tuple[str, Dict[str, str]]:
        for custom_object_type_code_dict in custom_object_type_code_dicts:
            if object_name in custom_object_type_code_dict:
                return custom_object_type_code_dict[object_name], cache_names
        return self._transform_object_type_name(
            object_name=object_name, default_name=default_name, cache_names=cache_names
        )

    def create_transformed_concept_link_type_name(
        self,
        concept_link_type_name: str,
        default_concept_link_type_name: str,
        concept_from_type_name: str,
        concept_to_type_name: str,
        transformed_concept_from_type_name: str,
        transformed_concept_to_type_name: str,
        link_cache_names: Dict[str, str],
        custom_type_code_storage: CustomTypeCodeStorage,
    ) -> Tuple[str, Dict[str, str]]:
        transformed_concept_link_type_name = custom_type_code_storage.get_concept_link_type_code(
            concept_from_type_name, concept_to_type_name, concept_link_type_name
        )
        if transformed_concept_link_type_name:
            return transformed_concept_link_type_name, link_cache_names
        return self._transform_object_type_name(
            object_name=self._generate_concept_link_name(
                transformed_concept_from_type_name, concept_link_type_name, transformed_concept_to_type_name
            ),
            cache_names=link_cache_names,
            default_name=default_concept_link_type_name,
        )

    def get_transformed_concept_type_name(
        self,
        concept_type_name: str,
        default_concept_name: str,
        concept_type_id: str,
        type_mapping: TypeMapping,
        custom_type_code_storage: CustomTypeCodeStorage,
        index_suffix: int = 1,
    ) -> Optional[str]:
        custom_concept_type_codes = custom_type_code_storage.concept_type_codes
        if concept_type_name in custom_concept_type_codes:
            return custom_concept_type_codes[concept_type_name]

        transformed_concept_name, _concept_cache_names = self._transform_object_type_name(
            object_name=concept_type_name, cache_names={}, default_name=default_concept_name, index_suffix=index_suffix
        )

        if transformed_concept_name not in type_mapping.concepts_types_mapping:
            return None
        if concept_type_id != type_mapping.concepts_types_mapping[transformed_concept_name].id:
            index_suffix += 1
            return self.get_transformed_concept_type_name(
                concept_type_name=concept_type_name,
                default_concept_name=default_concept_name,
                concept_type_id=concept_type_id,
                type_mapping=type_mapping,
                custom_type_code_storage=custom_type_code_storage,
                index_suffix=index_suffix,
            )
        return transformed_concept_name

    def _transform_object_type_name(
        self, object_name: str, default_name: str, cache_names: Dict[str, str], index_suffix: int = 1
    ) -> Tuple[str, Dict[str, str]]:
        _cache_names = cache_names.copy()
        transliterated_name = perform_transliteration(object_name)

        if not transliterated_name:
            transliterated_name = default_name

        if index_suffix > 1:
            transliterated_name += f"_{index_suffix}"

        if transliterated_name not in _cache_names:
            _cache_names[transliterated_name] = object_name
        elif object_name != _cache_names[transliterated_name]:
            index_suffix += 1
            return self._transform_object_type_name(
                object_name=object_name, cache_names=_cache_names, default_name=default_name, index_suffix=index_suffix
            )

        return transliterated_name, _cache_names
