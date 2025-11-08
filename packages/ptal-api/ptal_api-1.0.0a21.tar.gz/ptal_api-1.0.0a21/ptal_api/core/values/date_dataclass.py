from dataclasses import dataclass
from typing import Optional


@dataclass
class PartialDateValue:
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None


@dataclass
class PartialTimeValue:
    second: int
    minute: int
    hour: int


@dataclass
class PartialDateTimeValue:
    date: PartialDateValue
    time: Optional[PartialTimeValue] = None
