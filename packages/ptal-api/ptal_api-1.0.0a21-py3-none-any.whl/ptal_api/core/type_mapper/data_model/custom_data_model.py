import typing
from dataclasses import dataclass, field

from marshmallow import EXCLUDE, pre_load


@dataclass
class CustomTypeCodeStorage:
    concept_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_type_name, concept_type_code]
    concept_property_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_property_type_name, concept_property_type_code]
    concept_composite_property_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_composite_property_type_name, concept_composite_property_type_code]
    concept_composite_property_component_value_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_component_value_type_name, concept_component_value_type_code]
    concept_link_type_codes: typing.Dict[str, typing.List[typing.Tuple[str, str, str]]] = field(
        default_factory=dict
    )  # Dict[concept_link_type_name, List[Tuple[concept_from_type_name, concept_to_type_name, concept_link_type_code]]]
    concept_link_property_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_link_property_type_name, concept_link_property_type_code]
    concept_link_composite_property_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_link_composite_property_type_name, concept_link_composite_property_type_code]
    concept_link_composite_property_component_value_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_link_component_value_type_name, concept_link_component_value_type_code]
    concept_property_value_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[concept_property_value_type_name, concept_property_value_type_code]
    property_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[object_property_type_name, object_property_type_code]
    composite_property_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[object_composite_property_type_name, object_composite_property_type_code]
    any_property_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[object_any_property_type_name, object_any_property_type_code]
    composite_property_component_value_type_codes: typing.Dict[str, str] = field(
        default_factory=dict
    )  # Dict[object_component_value_type_name, object_component_value_type_code]

    def get_concept_link_type_code(
        self, concept_from_type_name: str, concept_to_type_name: str, concept_link_type_name: str
    ) -> typing.Optional[str]:
        if concept_link_type_name in self.concept_link_type_codes:
            for item in self.concept_link_type_codes[concept_link_type_name]:
                if item[0] == concept_from_type_name and item[1] == concept_to_type_name:
                    return item[2]
        return None

    @pre_load
    def exclude_null_value_items(self, input_data: dict, **_) -> dict:
        return {key: value for key, value in input_data.items() if value is not None}

    class Meta:
        ordered = True
        unknown = EXCLUDE
