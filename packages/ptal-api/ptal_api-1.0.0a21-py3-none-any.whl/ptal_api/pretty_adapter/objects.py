from dataclasses import dataclass, field
from typing import List, Optional, Union

from ptal_api.pretty_adapter.common import AccessLevel, Metadata
from ptal_api.pretty_adapter.object_types import ConceptType, LinkType, PropertyType
from ptal_api.pretty_adapter.property_values import Value


@dataclass
class Concept(Metadata):
    type: ConceptType
    access_level: AccessLevel
    notes: str
    markers: List[str]
    system_registration_date: int
    system_update_date: Optional[int]
    properties: List["Property"] = field(default_factory=list)
    links: List["Link"] = field(default_factory=list)
    related_documents: List["Document"] = field(default_factory=list)

    def add_link(self, link: "Link"):
        self.links.append(link)

    def add_property(self, concept_property: "Property"):
        self.properties.append(concept_property)


@dataclass
class Link:
    id: str
    type: LinkType
    concept_from: Concept
    concept_to: Concept
    access_level: AccessLevel
    notes: str
    properties: List["Property"] = field(default_factory=list)
    related_documents: List["Document"] = field(default_factory=list)
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)

    def add_property(self, link_property: "Property"):
        self.properties.append(link_property)


@dataclass
class Property:
    id: str
    type: PropertyType
    is_main: bool
    value: Value
    access_level: AccessLevel
    system_registration_date: int
    system_update_date: Optional[int] = None
    object_from: Union[Concept, Link, None] = None


@dataclass
class Document:
    id: str
    text: List[str] = field(default_factory=list)  # TODO: сделать списком FlatDocumentStructure
    uuid: Optional[str] = field(default=None)
    list_child: List["Document"] = field(default_factory=list)
    title: Optional[str] = None
    parent: Optional["Document"] = None
    external_url: Optional[str] = None
    related_concepts: List[Concept] = field(default_factory=list)
    related_links: List[Link] = field(default_factory=list)
    notes: Optional[str] = None
    markers: Optional[List[str]] = None
    publication_date: Optional[int] = None
    access_level: Optional[AccessLevel] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)


@dataclass
class Story:
    """There is no widespread support for Story in adapter"""

    id: str
    preview: Optional[str] = field(default=None)
    main: Optional[Document] = field(default=None)
    list_document: List[Document] = field(default_factory=list)
    title: Optional[str] = None
    access_level: Optional[AccessLevel] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)
