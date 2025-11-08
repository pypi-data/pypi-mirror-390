import typing
from dataclasses import dataclass, field

from marshmallow import EXCLUDE

from ptal_api.schema.api_schema import ConceptLinkType, ConceptPropertyType, ConceptPropertyValueType, ConceptType


@dataclass
class MappedCompositePropertyType:
    name: str
    component_values: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[component_value_type_code, component_value_type_name]

    class Meta:
        unknown = EXCLUDE


@dataclass
class MappedObjectType:
    id: typing.Optional[str] = field(default=None)
    properties: typing.Dict[str, str] = field(default_factory=dict)  # Dict[property_type_code, property_type_name]
    composite_properties: typing.Dict[str, MappedCompositePropertyType] = field(
        default_factory=dict
    )  # Dict[composite_property_type_code, mapped_composite_property]

    def add_mapped_property_type(self, property_type_code: str, property_type_name: str) -> None:
        self.properties[property_type_code] = property_type_name

    def add_mapped_composite_property_type(
        self, composite_property_type_code: str, mapped_composite_property_type: MappedCompositePropertyType
    ) -> None:
        self.composite_properties[composite_property_type_code] = mapped_composite_property_type

    class Meta:
        load_only = ("id",)
        unknown = EXCLUDE


@dataclass
class MappedConceptType(MappedObjectType):
    name: typing.Optional[str] = field(default=None)


@dataclass
class MappedConceptLinkType(MappedObjectType):
    source_type: typing.Optional[str] = field(default=None)
    target_type: typing.Optional[str] = field(default=None)
    old_relation_type: typing.Optional[str] = field(default=None)
    new_relation_type: typing.Optional[str] = field(default=None)


@dataclass
class CacheKeeper:
    concept_type_cache: typing.Dict[str, ConceptType] = field(
        metadata={"marshmallow_field": ConceptType}, default_factory=dict
    )  # Dict[concept_type_code, concept_type]
    concept_link_type_cache: typing.Dict[str, ConceptLinkType] = field(
        metadata={"marshmallow_field": ConceptLinkType}, default_factory=dict
    )  # Dict[concept_link_type_code, concept_link_type]
    concept_property_value_type_cache: typing.Dict[str, ConceptPropertyValueType] = field(
        metadata={"marshmallow_field": ConceptPropertyValueType}, default_factory=dict
    )  # Dict[concept_property_value_type_code, concept_property_value_type]
    concept_property_type_cache: typing.Dict[typing.Tuple[str, str], ConceptPropertyType] = field(
        metadata={"marshmallow_field": ConceptPropertyType}, default_factory=dict
    )  # Dict[(concept_type_code, concept_property_type_code), concept_property_type]
    concept_composite_property_type_cache: typing.Dict[typing.Tuple[str, str], ConceptPropertyType] = field(
        metadata={"marshmallow_field": ConceptPropertyType}, default_factory=dict
    )  # Dict[(concept_type_code, concept_composite_property_type_code), concept_property_type]
    concept_link_property_type_cache: typing.Dict[typing.Tuple[str, str], ConceptPropertyType] = field(
        metadata={"marshmallow_field": ConceptPropertyType}, default_factory=dict
    )  # Dict[(concept_link_type_code, concept_link_property_type_code), concept_property_type]
    concept_link_composite_property_type_cache: typing.Dict[typing.Tuple[str, str], ConceptPropertyType] = field(
        metadata={"marshmallow_field": ConceptPropertyType}, default_factory=dict
    )  # Dict[(concept_link_type_code, concept_link_composite_property_type_code), concept_property_type]

    def get_concept_type(self, concept_type_code: str) -> typing.Optional[ConceptType]:
        return self.concept_type_cache.get(concept_type_code, None)

    def get_concept_link_type(self, concept_link_type_code: str) -> typing.Optional[ConceptLinkType]:
        return self.concept_link_type_cache.get(concept_link_type_code, None)

    def get_concept_property_value_type(
        self, concept_property_value_type_code: str
    ) -> typing.Optional[ConceptPropertyValueType]:
        return self.concept_property_value_type_cache.get(concept_property_value_type_code, None)

    def get_concept_property_type(
        self, concept_type_code: str, property_type_code: str
    ) -> typing.Optional[ConceptPropertyType]:
        type_code_key = (concept_type_code, property_type_code)
        return self.concept_property_type_cache.get(type_code_key, None)

    def get_concept_composite_property_type(
        self, concept_type_code: str, composite_property_type_code: str
    ) -> typing.Optional[ConceptPropertyType]:
        type_code_key = (concept_type_code, composite_property_type_code)
        return self.concept_composite_property_type_cache.get(type_code_key, None)

    def get_concept_link_property_type(
        self, concept_link_type_code: str, property_type_code: str
    ) -> typing.Optional[ConceptPropertyType]:
        type_code_key = (concept_link_type_code, property_type_code)
        return self.concept_link_property_type_cache.get(type_code_key, None)

    def get_concept_link_composite_property_type(
        self, concept_link_type_code: str, composite_property_type_code: str
    ) -> typing.Optional[ConceptPropertyType]:
        type_code_key = (concept_link_type_code, composite_property_type_code)
        return self.concept_link_composite_property_type_cache.get(type_code_key, None)

    def add_concept_type(self, concept_type_code: str, concept_type: ConceptType) -> None:
        self.concept_type_cache[concept_type_code] = concept_type

    def add_concept_link_type(self, concept_link_type_code: str, concept_link_type: ConceptLinkType) -> None:
        self.concept_link_type_cache[concept_link_type_code] = concept_link_type

    def add_concept_property_value_type(
        self, concept_property_value_type_code: str, concept_property_value_type: ConceptPropertyValueType
    ) -> None:
        self.concept_property_value_type_cache[concept_property_value_type_code] = concept_property_value_type

    def add_concept_property_type(
        self, concept_type_code: str, property_type_code: str, concept_property_type: ConceptPropertyType
    ) -> None:
        self.concept_property_type_cache[(concept_type_code, property_type_code)] = concept_property_type

    def add_concept_composite_property_type(
        self, concept_type_code: str, composite_property_type_code: str, concept_property_type: ConceptPropertyType
    ) -> None:
        self.concept_composite_property_type_cache[
            (concept_type_code, composite_property_type_code)
        ] = concept_property_type

    def add_concept_link_property_type(
        self, concept_link_type_code: str, property_type_code: str, concept_property_type: ConceptPropertyType
    ) -> None:
        self.concept_link_property_type_cache[(concept_link_type_code, property_type_code)] = concept_property_type

    def add_concept_link_composite_property_type(
        self, concept_link_type_code: str, composite_property_type_code: str, concept_property_type: ConceptPropertyType
    ) -> None:
        self.concept_link_composite_property_type_cache[
            (concept_link_type_code, composite_property_type_code)
        ] = concept_property_type


@dataclass
class TypeMapping(CacheKeeper):
    concepts_types_mapping: typing.Dict[str, MappedConceptType] = field(default_factory=dict)
    relations_types_mapping: typing.List[MappedConceptLinkType] = field(default_factory=list)
    value_types_mapping: typing.Dict[str, str] = field(default_factory=dict)

    def get_concept_type_name(self, concept_type_code: str) -> typing.Optional[str]:
        if concept_type_code in self.concepts_types_mapping:
            return self.concepts_types_mapping.get(concept_type_code).name
        return None

    def get_concept_property_type_name(self, concept_type_code: str, property_type_code: str) -> typing.Optional[str]:
        if concept_type_code in self.concepts_types_mapping:
            mapped_concept_type = self.concepts_types_mapping.get(concept_type_code)
            return mapped_concept_type.properties.get(property_type_code, None)
        return None

    def get_concept_property_value_type_name(self, concept_property_value_type_code: str) -> typing.Optional[str]:
        return self.value_types_mapping.get(concept_property_value_type_code, None)

    def get_concept_link_type_name(self, concept_link_type_code: str) -> typing.Optional[str]:
        for relation_type_mapping in self.relations_types_mapping:
            if relation_type_mapping.old_relation_type == concept_link_type_code:
                return relation_type_mapping.new_relation_type
        return None

    def get_source_concept_type_code(self, concept_link_type_code: str) -> typing.Optional[str]:
        for relation_type_mapping in self.relations_types_mapping:
            if relation_type_mapping.old_relation_type == concept_link_type_code:
                return relation_type_mapping.source_type
        return None

    def get_target_concept_type_code(self, concept_link_type_code: str) -> typing.Optional[str]:
        for relation_type_mapping in self.relations_types_mapping:
            if relation_type_mapping.old_relation_type == concept_link_type_code:
                return relation_type_mapping.target_type
        return None

    def get_concept_link_property_type_name(
        self, concept_link_type_code: str, property_type_code: str
    ) -> typing.Optional[str]:
        for relation_type_mapping in self.relations_types_mapping:
            if relation_type_mapping.old_relation_type == concept_link_type_code:
                return relation_type_mapping.properties.get(property_type_code)
        return None

    def get_concept_composite_property_type_name(
        self, concept_type_code: str, composite_property_type_code: str
    ) -> typing.Optional[str]:
        if concept_type_code in self.concepts_types_mapping:
            mapped_concept_type = self.concepts_types_mapping.get(concept_type_code)
            if mapped_concept_type is None:
                return None
            if composite_property_type_code in mapped_concept_type.composite_properties:
                mapped_composite_property_type = mapped_concept_type.composite_properties.get(
                    composite_property_type_code
                )
                if mapped_composite_property_type:
                    return mapped_composite_property_type.name
            return None
        return None

    def get_concept_composite_property_component_value_type_name(
        self, concept_type_code: str, composite_property_type_code: str, component_value_type_code: str
    ) -> typing.Optional[str]:
        if concept_type_code in self.concepts_types_mapping:
            mapped_concept_type = self.concepts_types_mapping.get(concept_type_code)
            if mapped_concept_type is None:
                return None
            if composite_property_type_code in mapped_concept_type.composite_properties:
                mapped_composite_property = mapped_concept_type.composite_properties.get(composite_property_type_code)
                if mapped_composite_property:
                    return mapped_composite_property.component_values.get(component_value_type_code)
            return None
        return None

    def get_concept_composite_property_component_values(
        self, concept_type_code: str, composite_property_type_code: str
    ) -> typing.Optional[typing.Dict[str, str]]:
        if concept_type_code in self.concepts_types_mapping:
            mapped_concept_type = self.concepts_types_mapping.get(concept_type_code)
            if mapped_concept_type is None:
                return None
            if composite_property_type_code in mapped_concept_type.composite_properties:
                mapped_composite_property = mapped_concept_type.composite_properties.get(composite_property_type_code)
                if mapped_composite_property:
                    return mapped_composite_property.component_values
            return None
        return None

    def get_concept_link_composite_property_type_name(
        self, concept_link_type_code: str, composite_property_type_code: str
    ) -> typing.Optional[str]:
        for relation_type_mapping in self.relations_types_mapping:
            if relation_type_mapping.old_relation_type == concept_link_type_code:
                if composite_property_type_code in relation_type_mapping.composite_properties:
                    mapped_composite_property_type = relation_type_mapping.composite_properties.get(
                        composite_property_type_code
                    )
                    if mapped_composite_property_type:
                        return mapped_composite_property_type.name
                return None
        return None

    def get_concept_link_composite_property_component_value_type_name(
        self, concept_link_type_code: str, composite_property_type_code: str, component_value_type_code: str
    ) -> typing.Optional[str]:
        for relation_type_mapping in self.relations_types_mapping:
            if relation_type_mapping.old_relation_type == concept_link_type_code:
                if composite_property_type_code in relation_type_mapping.composite_properties:
                    mapped_composite_property = relation_type_mapping.composite_properties.get(
                        composite_property_type_code
                    )
                    if mapped_composite_property:
                        return mapped_composite_property.component_values.get(component_value_type_code)
                return None
        return None

    def get_concept_link_composite_property_component_values(
        self, concept_link_type_code: str, composite_property_type_code: str
    ) -> typing.Optional[typing.Dict[str, str]]:
        for relation_type_mapping in self.relations_types_mapping:
            if relation_type_mapping.old_relation_type == concept_link_type_code:
                mapped_composite_property_type = relation_type_mapping.composite_properties.get(
                    composite_property_type_code
                )
                if mapped_composite_property_type:
                    return mapped_composite_property_type.component_values
        return None

    def add_mapped_concept_type(self, concept_type_code: str, mapped_concept_type: MappedConceptType) -> None:
        self.concepts_types_mapping[concept_type_code] = mapped_concept_type

    def add_mapped_concept_link_type(self, mapped_concept_link_type: MappedConceptLinkType) -> None:
        self.relations_types_mapping.append(mapped_concept_link_type)

    def add_mapped_concept_property_value_type(
        self, concept_property_value_type_code: str, concept_property_value_type_name: str
    ) -> None:
        self.value_types_mapping[concept_property_value_type_code] = concept_property_value_type_name
