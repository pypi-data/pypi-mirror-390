from dataclasses import dataclass
from typing import Dict, Optional, Union

from .object_types import ComponentValueType


@dataclass
class LinkValue:
    link: str


@dataclass
class TimestampValue:
    unixtime: int


@dataclass
class Date:
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


@dataclass
class Time:
    hour: int
    minute: int
    second: int


@dataclass
class DateTime:
    date: Date
    time: Optional[Time] = None


# Составной тип значений характеристик
CompositeValueType = Dict[ComponentValueType, Union[str, int, float, DateTime, TimestampValue, LinkValue]]
# Возможные типы значений, поддерживаемые Талисманом
Value = Union[str, int, float, DateTime, TimestampValue, LinkValue, CompositeValueType]
