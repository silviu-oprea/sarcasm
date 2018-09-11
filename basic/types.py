import pprint
from abc import ABCMeta, abstractmethod
from typing import Iterable, Iterator, TypeVar, NamedTuple

T = TypeVar('T')
R = TypeVar('R')


class Comparable(metaclass=ABCMeta):
    @abstractmethod
    def __lt__(self, other) -> bool: ...


class EmptyIterator(Iterator[T]):
    def __next__(self):
        raise StopIteration

    def __iter__(self):
        while False:
            yield None


class Pair(NamedTuple):
    first: T
    second: R


class Printable:
    def __str__(self):
        return pprint.pformat(vars(self), indent=4)

    def __repr__(self):
        return pprint.pformat(vars(self), indent=4)


# === type utils ============================================================ #

def isiterable(obj) -> bool:
    return not isinstance(obj, (str, bytes)) and isinstance(obj, Iterable)
