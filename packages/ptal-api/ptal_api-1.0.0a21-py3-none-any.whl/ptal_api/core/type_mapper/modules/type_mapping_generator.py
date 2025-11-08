import logging
from typing import Any, Dict, Optional, Tuple

from ptal_api.adapter import TalismanAPIAdapter
from ptal_api.core.type_mapper.data_model.base_data_model import (
    MappedCompositePropertyType,
    MappedConceptLinkType,
    MappedConceptType,
    TypeMapping,
)
from ptal_api.core.type_mapper.data_model.config_data_model import DefaultTypeCodeStorage
from ptal_api.core.type_mapper.data_model.custom_data_model import CustomTypeCodeStorage
from ptal_api.core.type_mapper.modules.custom_data_handler import CustomDataHandler
from ptal_api.core.type_mapper.modules.object_name_transformer import ObjectTypeNameTransformer
from ptal_api.schema.api_schema import (
    CompositePropertyTypeFilterSettings,
    CompositePropertyValueTemplate,
    ConceptPropertyType,
    ConceptPropertyTypeFilterSettings,
)


class TypeMappingGenerator:
    def __init__(
        self,
        api_adapter: TalismanAPIAdapter,
        logger: logging.Logger,
        default_type_code_storage: Optional[DefaultTypeCodeStorage] = None,
        custom_type_code_storage: Optional[CustomTypeCodeStorage] = None,
    ):
        self._api_adapter = api_adapter
        self._logger = logger
        self._default_type_code_storage = (
            default_type_code_storage if default_type_code_storage else DefaultTypeCodeStorage()
        )
        self._custom_type_code_storage = (
            custom_type_code_storage if custom_type_code_storage else CustomTypeCodeStorage()
        )
        self._type_mapping: Optional[TypeMapping] = None
        self._name_transformer = ObjectTypeNameTransformer()

    @staticmethod
    def _initialize_object_type_cache_names(custom_object_type_codes: Dict[Any, Any]) -> Dict[Any, Any]:
        return {value: key for key, value in custom_object_type_codes.items()}

    @staticmethod
    def _is_property_type_composite(property_type: ConceptPropertyType) -> bool:
        return isinstance(property_type.value_type, CompositePropertyValueTemplate)

    def _process_concept_type_mapping(self) -> None:
        custom_concept_type_codes = self._custom_type_code_storage.concept_type_codes
        _concept_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(custom_concept_type_codes)

        for concept_type in self._api_adapter.get_all_concept_types():
            try:
                concept_type_name = concept_type.name

                (
                    transformed_concept_name,
                    _concept_cache_names,
                ) = self._name_transformer.create_transformed_object_type_name(
                    concept_type_name,
                    self._default_type_code_storage.concept_type_code,
                    _concept_cache_names,
                    custom_concept_type_codes,
                )

                self._type_mapping.add_mapped_concept_type(
                    transformed_concept_name, MappedConceptType(id=concept_type.id, name=concept_type_name)
                )
                self._type_mapping.add_concept_type(transformed_concept_name, concept_type)
                self._logger.debug(f"Processed a concept type with id equal to {concept_type.id}")
            except Exception as ex:
                self._logger.info(f"Failed to process a concept type with id equal to {concept_type.id}")
                self._logger.exception(ex)

    def _process_concept_property_type_mapping(self) -> None:
        custom_any_property_type_codes = self._custom_type_code_storage.any_property_type_codes
        custom_property_type_codes = self._custom_type_code_storage.property_type_codes
        custom_concept_property_type_codes = self._custom_type_code_storage.concept_property_type_codes
        _property_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            {**custom_any_property_type_codes, **custom_property_type_codes, **custom_concept_property_type_codes}
        )

        for transformed_concept_name, mapped_concept_type in self._type_mapping.concepts_types_mapping.items():
            for property_type in self._api_adapter.get_all_concept_property_types(
                filter_settings=ConceptPropertyTypeFilterSettings(concept_type_id=mapped_concept_type.id)
            ):
                try:
                    if self._is_property_type_composite(property_type):
                        continue

                    property_type_name = property_type.name

                    (
                        transformed_property_name,
                        _property_cache_names,
                    ) = self._name_transformer.create_transformed_object_type_name(
                        property_type_name,
                        self._default_type_code_storage.property_type_code,
                        _property_cache_names,
                        custom_concept_property_type_codes,
                        custom_property_type_codes,
                        custom_any_property_type_codes,
                    )

                    mapped_concept_type.add_mapped_property_type(transformed_property_name, property_type_name)
                    self._type_mapping.add_concept_property_type(
                        transformed_concept_name, transformed_property_name, property_type
                    )
                    self._logger.debug(
                        f"Processed a property type with id equal to {property_type.id}"
                        f" for a concept type with id equal to {mapped_concept_type.id}"
                    )
                except Exception as ex:
                    self._logger.info(
                        f"Failed to process a property type with id equal to {property_type.id}"
                        f" for a concept type with id equal to {mapped_concept_type.id}"
                    )
                    self._logger.exception(ex)

    def _process_concept_composite_property_type_mapping(self) -> None:
        custom_any_property_type_codes = self._custom_type_code_storage.any_property_type_codes
        custom_composite_property_type_codes = self._custom_type_code_storage.composite_property_type_codes
        custom_concept_composite_property_type_codes = (
            self._custom_type_code_storage.concept_composite_property_type_codes
        )
        custom_component_value_type_codes = self._custom_type_code_storage.composite_property_component_value_type_codes
        custom_concept_component_value_type_codes = (
            self._custom_type_code_storage.concept_composite_property_component_value_type_codes
        )
        _composite_property_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            {
                **custom_any_property_type_codes,
                **custom_composite_property_type_codes,
                **custom_concept_composite_property_type_codes,
            }
        )
        _component_value_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            {**custom_component_value_type_codes, **custom_concept_component_value_type_codes}
        )

        for transformed_concept_name, mapped_concept_type in self._type_mapping.concepts_types_mapping.items():
            for composite_property_type in self._api_adapter.get_all_concept_composite_property_types(
                filter_settings=CompositePropertyTypeFilterSettings(concept_type_id=mapped_concept_type.id)
            ):
                try:
                    composite_property_type_name = composite_property_type.name

                    (
                        transformed_composite_property_name,
                        _composite_property_cache_names,
                    ) = self._name_transformer.create_transformed_object_type_name(
                        composite_property_type_name,
                        self._default_type_code_storage.composite_property_type_code,
                        _composite_property_cache_names,
                        custom_concept_composite_property_type_codes,
                        custom_composite_property_type_codes,
                        custom_any_property_type_codes,
                    )

                    component_values, _component_value_cache_names = self._process_composite_component_value_types(
                        composite_property_type,
                        _component_value_cache_names,
                        custom_concept_component_value_type_codes,
                        custom_component_value_type_codes,
                    )

                    mapped_concept_type.add_mapped_composite_property_type(
                        transformed_composite_property_name,
                        MappedCompositePropertyType(
                            name=composite_property_type_name, component_values=component_values
                        ),
                    )
                    self._type_mapping.add_concept_composite_property_type(
                        transformed_concept_name, transformed_composite_property_name, composite_property_type
                    )
                    self._logger.debug(
                        f"Processed a composite property type with id equal to {composite_property_type.id}"
                        f" for a concept type with id equal to {mapped_concept_type.id}"
                    )
                except Exception as ex:
                    self._logger.info(
                        f"Failed to process a composite property type with id equal to {composite_property_type.id}"
                        f" for a concept type with id equal to {mapped_concept_type.id}"
                    )
                    self._logger.exception(ex)

    def _process_relation_type_mapping(self) -> None:
        custom_concept_link_type_codes = self._custom_type_code_storage.concept_link_type_codes
        _link_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            CustomDataHandler.unite_all_concept_link_mapping(custom_concept_link_type_codes)
        )

        for concept_link_type in self._api_adapter.get_all_concept_link_types():
            try:
                concept_link_type_name = concept_link_type.name
                concept_from_type_name = concept_link_type.concept_from_type.name
                concept_to_type_name = concept_link_type.concept_to_type.name
                transformed_concept_from_type_name = self._name_transformer.get_transformed_concept_type_name(
                    concept_from_type_name,
                    self._default_type_code_storage.concept_type_code,
                    concept_link_type.concept_from_type.id,
                    self._type_mapping,
                    self._custom_type_code_storage,
                )
                transformed_concept_to_type_name = self._name_transformer.get_transformed_concept_type_name(
                    concept_to_type_name,
                    self._default_type_code_storage.concept_type_code,
                    concept_link_type.concept_to_type.id,
                    self._type_mapping,
                    self._custom_type_code_storage,
                )

                (
                    transformed_concept_link_name,
                    _link_cache_names,
                ) = self._name_transformer.create_transformed_concept_link_type_name(
                    concept_link_type_name,
                    self._default_type_code_storage.concept_link_type_code,
                    concept_from_type_name,
                    concept_to_type_name,
                    transformed_concept_from_type_name,
                    transformed_concept_to_type_name,
                    _link_cache_names,
                    self._custom_type_code_storage,
                )

                self._type_mapping.add_mapped_concept_link_type(
                    MappedConceptLinkType(
                        id=concept_link_type.id,
                        source_type=transformed_concept_from_type_name,
                        target_type=transformed_concept_to_type_name,
                        old_relation_type=transformed_concept_link_name,
                        new_relation_type=concept_link_type_name,
                    )
                )
                self._type_mapping.add_concept_link_type(transformed_concept_link_name, concept_link_type)
                self._logger.debug(f"Processed a concept link type with id equal to {concept_link_type.id}")
            except Exception as ex:
                self._logger.info(f"Failed to process a concept link type with id equal to {concept_link_type.id}")
                self._logger.exception(ex)

    def _process_relation_property_type_mapping(self) -> None:
        custom_any_property_type_codes = self._custom_type_code_storage.any_property_type_codes
        custom_property_type_codes = self._custom_type_code_storage.property_type_codes
        custom_concept_link_property_type_codes = self._custom_type_code_storage.concept_link_property_type_codes
        _property_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            {**custom_any_property_type_codes, **custom_property_type_codes, **custom_concept_link_property_type_codes}
        )

        for mapped_concept_link_type in self._type_mapping.relations_types_mapping:
            for property_type in self._api_adapter.get_all_concept_link_property_types(
                filter_settings=ConceptPropertyTypeFilterSettings(concept_link_type_id=mapped_concept_link_type.id)
            ):
                try:
                    if self._is_property_type_composite(property_type):
                        continue

                    property_type_name = property_type.name

                    (
                        transformed_property_name,
                        _property_cache_names,
                    ) = self._name_transformer.create_transformed_object_type_name(
                        property_type_name,
                        self._default_type_code_storage.property_type_code,
                        _property_cache_names,
                        custom_concept_link_property_type_codes,
                        custom_property_type_codes,
                        custom_any_property_type_codes,
                    )

                    mapped_concept_link_type.add_mapped_property_type(transformed_property_name, property_type_name)
                    self._type_mapping.add_concept_link_property_type(
                        mapped_concept_link_type.old_relation_type, transformed_property_name, property_type
                    )
                    self._logger.debug(
                        f"Processed a property type with id equal to {property_type.id}"
                        f" for a concept link type with id equal to {mapped_concept_link_type.id}"
                    )
                except Exception as ex:
                    self._logger.info(
                        f"Failed to process a property type with id equal to {property_type.id}"
                        f" for a concept link type with id equal to {mapped_concept_link_type.id}"
                    )
                    self._logger.exception(ex)

    def _process_relation_composite_property_type_mapping(self) -> None:
        custom_any_property_type_codes = self._custom_type_code_storage.any_property_type_codes
        custom_composite_property_type_codes = self._custom_type_code_storage.composite_property_type_codes
        custom_concept_link_composite_property_type_codes = (
            self._custom_type_code_storage.concept_link_composite_property_type_codes
        )
        custom_component_value_type_codes = self._custom_type_code_storage.composite_property_component_value_type_codes
        custom_concept_link_component_value_type_codes = (
            self._custom_type_code_storage.concept_link_composite_property_component_value_type_codes
        )
        _composite_property_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            {
                **custom_any_property_type_codes,
                **custom_composite_property_type_codes,
                **custom_concept_link_composite_property_type_codes,
            }
        )
        _component_value_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            {**custom_component_value_type_codes, **custom_concept_link_component_value_type_codes}
        )

        for mapped_concept_link_type in self._type_mapping.relations_types_mapping:
            for composite_property_type in self._api_adapter.get_all_concept_link_composite_property_types(
                filter_settings=CompositePropertyTypeFilterSettings(link_type_id=mapped_concept_link_type.id)
            ):
                try:
                    composite_property_type_name = composite_property_type.name

                    (
                        transformed_composite_property_name,
                        _composite_property_cache_names,
                    ) = self._name_transformer.create_transformed_object_type_name(
                        composite_property_type_name,
                        self._default_type_code_storage.composite_property_type_code,
                        _composite_property_cache_names,
                        custom_concept_link_composite_property_type_codes,
                        custom_composite_property_type_codes,
                        custom_any_property_type_codes,
                    )

                    component_values, _component_value_cache_names = self._process_composite_component_value_types(
                        composite_property_type,
                        _component_value_cache_names,
                        custom_concept_link_component_value_type_codes,
                        custom_component_value_type_codes,
                    )

                    mapped_concept_link_type.add_mapped_composite_property_type(
                        transformed_composite_property_name,
                        MappedCompositePropertyType(
                            name=composite_property_type_name, component_values=component_values
                        ),
                    )
                    self._type_mapping.add_concept_link_composite_property_type(
                        mapped_concept_link_type.old_relation_type,
                        transformed_composite_property_name,
                        composite_property_type,
                    )
                    self._logger.debug(
                        f"Processed a composite property type with id equal to {composite_property_type.id}"
                        f" for a concept link type with id equal to {mapped_concept_link_type.id}"
                    )
                except Exception as ex:
                    self._logger.info(
                        f"Failed to process a composite property type with id equal to {composite_property_type.id}"
                        f" for a concept link type with id equal to {mapped_concept_link_type.id}"
                    )
                    self._logger.exception(ex)

    def _process_concept_property_value_type_mapping(self) -> None:
        custom_concept_property_value_type_codes = self._custom_type_code_storage.concept_property_value_type_codes
        _property_value_cache_names: Dict[str, str] = self._initialize_object_type_cache_names(
            custom_concept_property_value_type_codes
        )

        for property_value_type in self._api_adapter.get_all_concept_property_value_types():
            try:
                property_value_type_name = property_value_type.name

                (
                    transformed_property_value_name,
                    _property_value_cache_names,
                ) = self._name_transformer.create_transformed_object_type_name(
                    property_value_type_name,
                    self._default_type_code_storage.concept_property_value_type_code,
                    _property_value_cache_names,
                    custom_concept_property_value_type_codes,
                )

                self._type_mapping.add_mapped_concept_property_value_type(
                    transformed_property_value_name, property_value_type_name
                )
                self._type_mapping.add_concept_property_value_type(transformed_property_value_name, property_value_type)
                self._logger.debug(f"Processed a concept property value type with id equal to {property_value_type.id}")
            except Exception as ex:
                self._logger.info(
                    f"Failed to process a concept property value type with id equal to {property_value_type.id}"
                )
                self._logger.exception(ex)

    def _process_composite_component_value_types(
        self,
        composite_property_type: ConceptPropertyType,
        component_value_type_cache_names: Dict[str, str],
        custom_object_component_value_type_codes: Dict[str, str],
        custom_component_value_type_codes: Dict[str, str],
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        component_value_types: Dict[str, str] = {}  # Dict[component_value_type_code, component_value_type_name]
        _component_value_type_cache_names = component_value_type_cache_names.copy()

        for component_value_type in composite_property_type.value_type.component_value_types:
            try:
                component_value_type_name = component_value_type.name

                (
                    transformed_component_value_name,
                    _component_value_type_cache_names,
                ) = self._name_transformer.create_transformed_object_type_name(
                    component_value_type_name,
                    self._default_type_code_storage.composite_property_component_value_type_code,
                    _component_value_type_cache_names,
                    custom_object_component_value_type_codes,
                    custom_component_value_type_codes,
                )

                component_value_types[transformed_component_value_name] = component_value_type_name
                self._logger.debug(
                    f"Processed a component value type with id equal to {component_value_type.id}"
                    f" for a composite property type with id equal to {composite_property_type.id}"
                )
            except Exception as ex:
                self._logger.debug(
                    f"Failed to process a component value type with id equal to {component_value_type.id}"
                    f" for a composite property type with id equal to {composite_property_type.id}"
                )
                self._logger.exception(ex)
        return component_value_types, _component_value_type_cache_names

    def process_type_mapping(self) -> TypeMapping:
        self._type_mapping = TypeMapping()
        self._process_concept_type_mapping()
        self._process_concept_property_type_mapping()
        self._process_concept_composite_property_type_mapping()
        self._process_relation_type_mapping()
        self._process_relation_property_type_mapping()
        self._process_relation_composite_property_type_mapping()
        self._process_concept_property_value_type_mapping()
        return self._type_mapping
