from functools import wraps
from types import GeneratorType
from typing import Any, Callable, Iterator, List, Optional, Union

from ptal_api.core.values.date_dataclass import PartialDateValue
from ptal_api.core.values.value_mapping import (
    COMPOSITE_VALUE,
    DATE_VALUE,
    DOUBLE_VALUE,
    INT_VALUE,
    LINK_VALUE,
    STRING_VALUE,
    TIMESTAMP_VALUE,
    get_map_helper,
)
from ptal_api.pretty_adapter.object_types import (
    BaseValueType,
    ComponentValueType,
    CompositeValueType,
    ConceptType,
    LinkType,
    PropertyType,
)
from ptal_api.pretty_adapter.objects import Concept, Document, Link, Property, Story
from ptal_api.pretty_adapter.property_values import Date, DateTime, LinkValue, Time, TimestampValue, Value
from ptal_api.schema import api_schema, utils_api_schema
from .common import AccessLevel, gmap


class Transformer:
    @staticmethod
    def object_schema_to_object(
        object_schema,
    ) -> Union[Concept, Link, Property, ConceptType, LinkType, PropertyType, BaseValueType, CompositeValueType]:
        """Transform any schema object to its pretty_adapter analog"""
        types = [
            ((api_schema.Concept, utils_api_schema.Concept), Transformer.concept_schema_to_concept),
            ((api_schema.ConceptProperty, utils_api_schema.ConceptProperty), Transformer.property_schema_to_property),
            ((api_schema.ConceptLink, utils_api_schema.ConceptLink), Transformer.link_schema_to_link),
            ((api_schema.ConceptType, utils_api_schema.ConceptType), Transformer.concept_type_schema_to_concept_type),
            ((api_schema.ConceptLinkType, utils_api_schema.ConceptLinkType), Transformer.link_type_schema_to_link_type),
            (
                (api_schema.ConceptPropertyType, utils_api_schema.ConceptPropertyType),
                Transformer.property_type_schema_to_property_type,
            ),
            (
                (api_schema.ConceptPropertyValueType, utils_api_schema.ConceptPropertyValueType),
                Transformer.base_value_type_schema_to_base_value_type,
            ),
            (
                (api_schema.CompositePropertyValueTemplate, utils_api_schema.CompositePropertyValueTemplate),
                Transformer.composite_value_type_schema_to_composite_value_type,
            ),
        ]
        for schema_type, transformer in types:
            if isinstance(object_schema, schema_type):
                return transformer(object_schema)
        return object_schema

    @staticmethod
    def value_to_schema_value_type(value) -> str:
        if isinstance(value, str):
            return STRING_VALUE
        if isinstance(value, int):
            return INT_VALUE
        if isinstance(value, (Date, DateTime)):
            return DATE_VALUE
        if isinstance(value, TimestampValue):
            return TIMESTAMP_VALUE
        if isinstance(value, LinkValue):
            return LINK_VALUE
        if isinstance(value, float):
            return DOUBLE_VALUE
        if isinstance(value, dict):
            return COMPOSITE_VALUE
        raise NotImplementedError(f"Type {type(value)} is not supported")

    @staticmethod
    def value_schema_to_value(value_schema: Any, value_type: str) -> Value:
        if value_type == STRING_VALUE:
            return str(value_schema.value)
        if value_type == INT_VALUE:
            return int(value_schema.number)
        if value_type == LINK_VALUE:
            return LinkValue(link=value_schema.link)
        if value_type == DOUBLE_VALUE:
            return float(value_schema.value.double)
        if value_type == DATE_VALUE:
            date_value = value_schema.date
            time_value = getattr(value_schema, "time", None)
            time_input = (
                Time(hour=time_value.hour, minute=time_value.minute, second=time_value.second) if time_value else None
            )
            return DateTime(
                date=Date(
                    year=getattr(date_value, "year", None),
                    month=getattr(date_value, "month", None),
                    day=getattr(date_value, "day", None),
                ),
                time=time_input,
            )
        if value_type == TIMESTAMP_VALUE:
            return TimestampValue(unixtime=value_schema.unixtime)
        if value_type == COMPOSITE_VALUE:
            return {
                ComponentValueType(
                    id=nv.id,
                    name=nv.property_value_type.name,
                    value_type=Transformer.base_value_type_schema_to_base_value_type(nv.property_value_type.value_type),
                    system_registration_date=getattr(nv, "system_registration_date", None),
                    system_update_date=getattr(nv, "system_update_date", None),
                ): Transformer.value_schema_to_value(nv.value, nv.property_value_type.value_type.value_type)
                for nv in value_schema.list_value
            }
        raise NotImplementedError(f"not implemented value type {value_type}")

    @staticmethod
    def pretty_value_to_adapter_value(value: Value) -> Any:
        adapter_value = value
        if isinstance(value, DateTime):
            adapter_value = PartialDateValue(year=value.date.year, month=value.date.month, day=value.date.day)
        elif isinstance(value, TimestampValue):
            adapter_value = value.unixtime
        elif isinstance(value, LinkValue):
            adapter_value = value.link
        return adapter_value

    @staticmethod
    def value_to_value_input(value: Value) -> List[api_schema.ComponentValueInput]:
        """Pretty_adapter value to value_input"""
        if not isinstance(value, dict):
            value_input = [
                api_schema.ComponentValueInput(
                    value=get_map_helper(Transformer.value_to_schema_value_type(value)).get_value_input(
                        Transformer.pretty_value_to_adapter_value(value)
                    )
                )
            ]
        else:
            value_input = [
                api_schema.ComponentValueInput(
                    id=named_value[0].id,
                    value=get_map_helper(Transformer.value_to_schema_value_type(named_value[1])).get_value_input(
                        Transformer.pretty_value_to_adapter_value(named_value[1])
                    ),
                )
                for named_value in value.items()
            ]
        return value_input

    @staticmethod
    def access_level_schema_to_access_level(
        access_level_schema: Union[api_schema.AccessLevel, utils_api_schema.AccessLevel]
    ) -> AccessLevel:
        return AccessLevel(id=access_level_schema.id, name=access_level_schema.name, order=access_level_schema.order)

    @staticmethod
    def property_schema_to_property(
        property_schema: api_schema.ConceptProperty,
        property_type_code: Optional[str] = None,
        object_from: Union[Concept, Link, None] = None,
    ) -> Property:
        prop_type = Transformer.property_type_schema_to_property_type(property_schema.property_type, property_type_code)
        if isinstance(prop_type.value_type, CompositeValueType):
            value_type = COMPOSITE_VALUE
        else:
            value_type = property_schema.property_type.value_type.value_type
        return Property(
            id=property_schema.id,
            type=prop_type,
            value=Transformer.value_schema_to_value(property_schema.value, value_type),
            object_from=object_from,
            is_main=property_schema.is_main,
            system_registration_date=property_schema.system_registration_date,
            system_update_date=getattr(property_schema, "system_update_date", None),
            access_level=Transformer.access_level_schema_to_access_level(property_schema.access_level),
        )

    @staticmethod
    def base_value_type_schema_to_base_value_type(
        value_type_schema: api_schema.ConceptPropertyValueType, type_code: Optional[str] = None
    ) -> BaseValueType:
        return BaseValueType(
            id=value_type_schema.id,
            name=value_type_schema.name,
            code=type_code,
            value_type=value_type_schema.value_type,
            system_registration_date=getattr(value_type_schema, "system_registration_date", None),
            system_update_date=getattr(value_type_schema, "system_update_date", None),
        )

    @staticmethod
    def composite_value_type_schema_to_composite_value_type(
        value_type_schema: api_schema.CompositePropertyValueTemplate, type_code: Optional[str] = None
    ) -> CompositeValueType:
        component_value_types: List[ComponentValueType] = []
        for comp in getattr(value_type_schema, "component_value_types", []):
            value_type = Transformer.base_value_type_schema_to_base_value_type(comp.value_type)
            component_value_types.append(
                ComponentValueType(
                    id=comp.id,
                    name=comp.name,
                    value_type=value_type,
                    system_registration_date=getattr(comp, "system_registration_date", None),
                    system_update_date=getattr(comp, "system_update_date", None),
                )
            )
        return CompositeValueType(
            id=value_type_schema.id,
            name=value_type_schema.name,
            code=type_code,
            component_value_types=component_value_types,
            system_registration_date=getattr(value_type_schema, "system_registration_date", None),
            system_update_date=getattr(value_type_schema, "system_update_date", None),
        )

    @staticmethod
    def property_type_schema_to_property_type(
        type_schema: Union[api_schema.ConceptType, api_schema.ConceptPropertyType, api_schema.ConceptLinkType],
        type_code: Optional[str] = None,
    ) -> PropertyType:
        value_type: Union[CompositeValueType, BaseValueType, None] = None
        if hasattr(type_schema, "value_type"):
            if isinstance(
                type_schema.value_type, (api_schema.ConceptPropertyValueType, utils_api_schema.ConceptPropertyValueType)
            ):
                value_type = Transformer.base_value_type_schema_to_base_value_type(type_schema.value_type)
            elif isinstance(
                type_schema.value_type,
                (api_schema.CompositePropertyValueTemplate, utils_api_schema.CompositePropertyValueTemplate),
            ):
                value_type = Transformer.composite_value_type_schema_to_composite_value_type(type_schema.value_type)
        return PropertyType(
            id=type_schema.id,
            name=type_schema.name,
            code=type_code,
            value_type=value_type,
            system_registration_date=getattr(type_schema, "system_registration_date", None),
            system_update_date=getattr(type_schema, "system_update_date", None),
        )

    @staticmethod
    def concept_type_schema_to_concept_type(
        type_schema: api_schema.ConceptType, type_code: Optional[str] = None
    ) -> ConceptType:
        return ConceptType(
            id=type_schema.id,
            name=type_schema.name,
            code=type_code,
            system_registration_date=getattr(type_schema, "system_registration_date", None),
            system_update_date=getattr(type_schema, "system_update_date", None),
        )

    @staticmethod
    def link_type_schema_to_link_type(
        type_schema: api_schema.ConceptLinkType, type_code: Optional[str] = None
    ) -> LinkType:
        return LinkType(
            id=type_schema.id,
            name=type_schema.name,
            code=type_code,
            is_directed=type_schema.is_directed,
            system_registration_date=getattr(type_schema, "system_registration_date", None),
            system_update_date=getattr(type_schema, "system_update_date", None),
        )

    @staticmethod
    def link_schema_to_link(
        link_schema: api_schema.ConceptLink,
        link_type_code: Optional[str] = None,
    ) -> Link:
        link = Link(
            id=link_schema.id,
            type=Transformer.link_type_schema_to_link_type(link_schema.concept_link_type, link_type_code),
            concept_from=Transformer.concept_schema_to_concept(link_schema.concept_from),
            concept_to=Transformer.concept_schema_to_concept(link_schema.concept_to),
            properties=[],
            system_registration_date=getattr(link_schema, "system_registration_date", None),
            system_update_date=getattr(link_schema, "system_update_date", None),
            access_level=Transformer.access_level_schema_to_access_level(link_schema.access_level),
            notes=link_schema.notes,
        )
        if hasattr(link_schema, "pagination_concept_link_property"):
            for prop in link_schema.pagination_concept_link_property.list_concept_property:
                link.add_property(Transformer.property_schema_to_property(property_schema=prop, object_from=link))
        return link

    @staticmethod
    def concept_schema_to_concept(concept_schema: api_schema.Concept, concept_code: Optional[str] = None) -> Concept:
        concept = Concept(
            id=concept_schema.id,
            type=Transformer.concept_type_schema_to_concept_type(concept_schema.concept_type, concept_code),
            name=concept_schema.name,
            notes=concept_schema.notes,
            markers=concept_schema.markers,
            properties=[],
            links=[],
            system_registration_date=concept_schema.system_registration_date,
            system_update_date=getattr(concept_schema, "system_update_date", None),
            access_level=Transformer.access_level_schema_to_access_level(concept_schema.access_level),
        )
        if hasattr(concept_schema, "pagination_concept_property"):
            for prop in concept_schema.pagination_concept_property.list_concept_property:
                concept.add_property(Transformer.property_schema_to_property(property_schema=prop))
        if hasattr(concept_schema, "pagination_concept_link"):
            for link in concept_schema.pagination_concept_link.list_concept_link:
                concept.add_link(Transformer.link_schema_to_link(link_schema=link))
        return concept

    # @staticmethod
    # def component_values_to_object_types(value: ValueType, property_type: ObjectType) -> ValueType:

    @staticmethod
    def flat_document_structure_to_str(flat_document_structure: api_schema.FlatDocumentStructure) -> str:
        return flat_document_structure.text  # TODO: нормально обрабатывать flat_document_structure

    @staticmethod
    def document_schema_to_document(document_schema: api_schema.Document) -> Document:
        parent = None
        if hasattr(document_schema, "parent"):
            parent = Transformer.document_schema_to_document(document_schema.parent)
        return Document(
            id=document_schema.id,
            text=list(map(Transformer.flat_document_structure_to_str, document_schema.text)),
            list_child=list(map(Transformer.document_schema_to_document, document_schema.list_child)),
            title=getattr(document_schema, "title", None),
            parent=parent,
            external_url=getattr(document_schema, "external_url", None),
            uuid=getattr(document_schema, "uuid", None),
            notes=getattr(document_schema, "notes", None),
            markers=getattr(document_schema, "markers", None),
            system_registration_date=getattr(document_schema, "system_registration_date", None),
            system_update_date=getattr(document_schema, "system_update_date", None),
            publication_date=getattr(document_schema, "publication_date", None),
            access_level=Transformer.access_level_schema_to_access_level(document_schema.access_level),
            # concept_facts=,
            # link_facts=,
            # facts=
        )

    @staticmethod
    def story_schema_to_story(story_schema: api_schema.Story) -> Story:
        return Story(
            id=story_schema.id,
            preview=story_schema.preview,
            main=Transformer.document_schema_to_document(story_schema.main),
            list_document=list(map(Transformer.document_schema_to_document, story_schema.list_document)),
            title=getattr(story_schema, "title", None),
            system_registration_date=getattr(story_schema, "system_registration_date", None),
            system_update_date=getattr(story_schema, "system_update_date", None),
        )


def prettify(func: Callable) -> Callable:
    """Can decorate all TalismanAPIAdapter methods that return Concept, ConceptProperty, ConceptLink,
    ConceptLinkProperty, ConceptType, ConceptLinkType, ConceptPropertyType, any values and value types, and any
    iterators or generators that contains these objects"""

    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        """Transform adapter methods output (schema objects) to pretty_adapter objects
        if obj.prettify_output (TalismanAPIAdapter field) is True
        """
        result = func(obj, *args, **kwargs)
        if not obj.prettify_output:
            return result
        if isinstance(result, GeneratorType):
            return gmap(Transformer.object_schema_to_object, result)
        if isinstance(result, Iterator):
            return [*gmap(Transformer.object_schema_to_object, result)]
        return Transformer.object_schema_to_object(result)

    return wrapper
