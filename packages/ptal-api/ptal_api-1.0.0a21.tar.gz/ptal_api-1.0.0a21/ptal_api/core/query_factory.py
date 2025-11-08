import functools
import typing

from sgqlc.operation import Operation
from sgqlc.types import Arg

PREFIX = "ptal_"
ANON = "anonymous"


def make_operation(
    cls, prettified_name: typing.Optional[str] = None, variables: typing.Optional[typing.Dict[str, Arg]] = None
) -> Operation:
    of = functools.partial(Operation, cls)
    pof = functools.partial(of, name=f"{PREFIX}{prettified_name if prettified_name else ANON}")
    return pof(variables=variables) if variables else pof()
