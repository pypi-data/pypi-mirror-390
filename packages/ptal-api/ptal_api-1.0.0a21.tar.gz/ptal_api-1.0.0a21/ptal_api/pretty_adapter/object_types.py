from dataclasses import dataclass, field
from typing import List, Optional, Union

from .common import Metadata


@dataclass
class ConceptType(Metadata):
    code: Optional[str] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)


@dataclass
class LinkType(Metadata):
    is_directed: bool
    code: Optional[str] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)


@dataclass
class BaseValueType(Metadata):
    """Base type for values like 'string', 'int', 'link', 'date'"""

    value_type: Optional[str] = None
    code: Optional[str] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)


@dataclass(frozen=True)
class ComponentValueType:
    """Key from composite value type"""

    id: str
    name: str
    value_type: Optional[BaseValueType] = None
    code: Optional[str] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id


@dataclass
class CompositeValueType(Metadata):
    component_value_types: List[ComponentValueType] = field(default_factory=list)
    code: Optional[str] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)


@dataclass
class PropertyType(Metadata):
    value_type: Union[CompositeValueType, BaseValueType, None] = None
    code: Optional[str] = None
    system_registration_date: Optional[int] = field(default=None)
    system_update_date: Optional[int] = field(default=None)
