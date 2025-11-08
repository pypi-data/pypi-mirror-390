import typing
from dataclasses import dataclass, field


@dataclass
class DefaultTypeCodeStorage:
    concept_type_code: str = field(default="concept_code")
    concept_link_type_code: str = field(default="concept_link_code")
    property_type_code: str = field(default="property_code")
    composite_property_type_code: str = field(default="composite_property_code")
    composite_property_component_value_type_code: str = field(default="component_value_code")
    concept_property_value_type_code: str = field(default="property_value_code")


@dataclass
class FileGenerationSettings:
    default_file_path: str = field(default="./type_mapping/type_mapping.json")
    indent: int = field(default=4)
    sort_keys: bool = field(default=True)
    generated_fields: typing.Set[str] = field(
        default_factory=lambda: {"concepts_types_mapping", "relations_types_mapping", "value_types_mapping"}
    )
