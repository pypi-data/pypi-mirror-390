import datetime
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Type, Union

from sgqlc.types import Input

from ptal_api.schema.api_schema import (
    Date,
    DateInput,
    DateTimeInput,
    DateTimeValue,
    DoubleValueInput,
    IntValueInput,
    LinkValueInput,
    StringValueInput,
    TimeInput,
    TimestampValueInput,
    ValueInput,
)
from .date_dataclass import PartialDateTimeValue, PartialDateValue


class AbstractValueMapper(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def get_value_input(value: Any) -> Input:
        pass

    @staticmethod
    @abstractmethod
    def get_tdm_value_format(value: Any) -> Dict:
        pass


class StringValueMapper(AbstractValueMapper):
    @staticmethod
    def get_value_input(value: str) -> Input:
        string_input = StringValueInput()
        string_input.str = value

        value_input = ValueInput()
        value_input.string_value_input = string_input
        return value_input

    @staticmethod
    def get_tdm_value_format(value: str) -> Dict:
        return {"value": value}


class IntValueMapper(AbstractValueMapper):
    @staticmethod
    def get_value_input(value: int) -> Input:
        int_input = IntValueInput()
        int_input.int = value

        value_input = ValueInput()
        value_input.int_value_input = int_input
        return value_input

    @staticmethod
    def get_tdm_value_format(value: int) -> Dict:
        return {"value": value}


class DoubleValueMapper(AbstractValueMapper):
    @staticmethod
    def get_value_input(value: float) -> Input:
        double_input = DoubleValueInput()
        double_input.double = value

        value_input = ValueInput()
        value_input.double_value_input = double_input
        return value_input

    @staticmethod
    def get_tdm_value_format(value: float) -> Dict:
        return {"value": value}


class DateValueMapper(AbstractValueMapper):
    @staticmethod
    def get_value_input(
        value: Union[Date, datetime.date, datetime.datetime, DateTimeValue, PartialDateTimeValue, PartialDateValue]
    ) -> Input:
        date_time_value_input = DateTimeInput()

        if isinstance(value, datetime.date):
            date_value = value
            time_value = value if isinstance(value, datetime.datetime) else None
        else:
            date_value = value.date
            time_value = getattr(value, "time", None)

        date_input = DateInput()
        date_input.day = getattr(date_value, "day", None)
        date_input.month = getattr(date_value, "month", None)
        date_input.year = getattr(date_value, "year", None)
        date_time_value_input.date = date_input

        if time_value is not None:
            time_input = TimeInput()
            time_input.second = getattr(time_value, "second", None)
            time_input.minute = getattr(time_value, "minute", None)
            time_input.hour = getattr(time_value, "hour", None)
            if all(val is not None for val in (time_input.second, time_input.minute, time_input.hour)):
                date_time_value_input.time = time_input

        value_input = ValueInput()
        value_input.date_time_value_input = date_time_value_input
        return value_input

    @staticmethod
    def get_tdm_value_format(
        value: Union[Date, datetime.date, datetime.datetime, DateTimeValue, PartialDateTimeValue, PartialDateValue]
    ) -> Dict:
        if isinstance(value, datetime.date):
            date_value = value
            time_value = value if isinstance(value, datetime.datetime) else None
        else:
            date_value = value.date
            time_value = getattr(value, "time", None)

        if time_value is not None and all(
            val is not None
            for val in (
                getattr(time_value, "second", None),
                getattr(time_value, "minute", None),
                getattr(time_value, "hour", None),
            )
        ):
            time_obj = {
                "second": time_value.second,
                "minute": time_value.minute,
                "hour": time_value.hour,
            }
        else:
            time_obj = None
        return {
            "date": {
                "day": getattr(date_value, "day", None),
                "month": getattr(date_value, "month", None),
                "year": getattr(date_value, "year", None),
            },
            "time": time_obj,
        }


class TimestampValueMapper(AbstractValueMapper):
    @staticmethod
    def get_value_input(value: int) -> Input:
        timestamp_input = TimestampValueInput()
        timestamp_input.value = value

        value_input = ValueInput()
        value_input.timestamp_value_input = timestamp_input
        return value_input

    @staticmethod
    def get_tdm_value_format(value: int) -> Dict:
        return {"value": value}


class LinkValueMapper(AbstractValueMapper):
    @staticmethod
    def get_value_input(value: str) -> Input:
        link_input = LinkValueInput()
        link_input.link = value

        value_input = ValueInput()
        value_input.link_value_input = link_input
        return value_input

    @staticmethod
    def get_tdm_value_format(value: str) -> Dict:
        return {"link": value}


STRING_VALUE = "String"
INT_VALUE = "Int"
DOUBLE_VALUE = "Double"
DATE_VALUE = "Date"
TIMESTAMP_VALUE = "Timestamp"
LINK_VALUE = "Link"
COMPOSITE_VALUE = "CompositeValue"


def get_map_helper(value_type: str) -> Type[AbstractValueMapper]:
    if value_type == STRING_VALUE:
        return StringValueMapper
    if value_type == INT_VALUE:
        return IntValueMapper
    if value_type == DOUBLE_VALUE:
        return DoubleValueMapper
    if value_type == DATE_VALUE:
        return DateValueMapper
    if value_type == TIMESTAMP_VALUE:
        return TimestampValueMapper
    if value_type == LINK_VALUE:
        return LinkValueMapper
    raise NotImplementedError(f"{value_type} type not implemented")
