from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass
class Metadata:
    id: str
    name: str


@dataclass
class AccessLevel:
    id: str
    name: str
    order: int


def gmap(func: Callable, objects: Iterable):
    """Like a map function, but returns generator"""
    for obj in objects:
        yield func(obj)
