from ptal_api.adapter import TalismanAPIAdapter
from ptal_api.pretty_adapter.objects import Concept, Link, Property
from ptal_api.pretty_adapter.property_values import Value
from ptal_api.pretty_adapter.transformer import Transformer
from .object_types import LinkType, PropertyType


class PrettyTalismanAPIAdapter:
    """Take and return pretty_adapter objects"""

    def __init__(self, adapter: TalismanAPIAdapter):
        self._adapter: TalismanAPIAdapter = adapter

    def update_concept(self, concept: Concept) -> Concept:
        return Transformer.concept_schema_to_concept(
            self._adapter._update_concept(
                concept_id=concept.id,
                name=concept.name,
                concept_type_id=concept.type.id,
                markers=concept.markers,
                notes=concept.notes,
                access_level_id=concept.access_level.id,
            ),
            concept.type.code,
        )

    def update_link(self, link: Link) -> Link:
        return Transformer.link_schema_to_link(
            self._adapter._update_link(link_id=link.id, access_level_id=link.access_level.id, notes=link.notes),
            link.type.code,
        )

    def update_property(self, concept_property: Property) -> Property:
        cp = self._adapter._update_concept_property_with_input(
            property_id=concept_property.id,
            is_main=concept_property.is_main,
            value_input=Transformer.value_to_value_input(concept_property.value),
            access_level_id=concept_property.access_level.id,
        )
        return Transformer.property_schema_to_property(cp, concept_property.type.code, concept_property.object_from)

    def add_link(self, concept_from: Concept, concept_to: Concept, link_type: LinkType) -> Link:
        rel = self._adapter._add_relation_by_id(from_id=concept_from.id, to_id=concept_to.id, link_type_id=link_type.id)
        link = Transformer.link_schema_to_link(rel, link_type.code)
        link.concept_from = concept_from
        link.concept_to = concept_to
        return link

    def add_concept_property(
        self,
        concept: Concept,
        property_type: PropertyType,
        value: Value,
        is_main: bool = False,
    ) -> Property:
        prop = self._adapter._add_concept_property_with_input_by_id(
            concept_id=concept.id,
            property_type_id=property_type.id,
            value_input=Transformer.value_to_value_input(value),
            is_main=is_main,
        )
        cp = Transformer.property_schema_to_property(prop, property_type_code=property_type.code, object_from=concept)
        concept.add_property(cp)
        return cp

    def add_link_property(
        self,
        link: Link,
        property_type: PropertyType,
        value: Value,
        is_main: bool = False,
    ) -> Property:
        prop = self._adapter._add_link_property_with_input_by_id(
            link_id=link.id,
            property_type_id=property_type.id,
            value_input=Transformer.value_to_value_input(value),
            is_main=is_main,
        )
        lp = Transformer.property_schema_to_property(prop, property_type_code=property_type.code, object_from=link)
        link.add_property(lp)
        return lp

    def delete_concept(self, concept: Concept) -> bool:
        return self._adapter.delete_concept(concept.id)

    def delete_property(self, concept_property: Property) -> bool:
        return self._adapter.delete_concept_property(concept_property.id)

    def delete_link(self, link: Link) -> bool:
        return self._adapter.delete_concept_link(link.id)

    def delete_link_property(self, link_property: Property) -> bool:
        return self._adapter.delete_concept_link_property(link_property.id)
