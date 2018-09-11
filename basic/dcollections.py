from typing import Callable, TypeVar, Set, Iterable, Iterator, List

from basic import functions, types
from basic.ditertools import zip_with_index

T = TypeVar('T')
CT = TypeVar('CT', bound=types.Comparable)


class orderedset(Set[T]):
    def __init__(self,
                 iterable: Iterable[T] = types.EmptyIterator[T](),
                 key: Callable[[T], CT] = functions.id):
        self._key = key
        super().__init__(iterable)

    def __iter__(self) -> Iterator[T]:
        sorted_items = sorted(set.__iter__(self), key=self._key)
        return iter(sorted_items)


class setlist(List[T]):
    def __init__(self, lst):
        super().__init__(lst)
        self._item_to_idx = dict(zip_with_index(self))

    def __contains__(self, item):
        return item in self._item_to_idx

    def index(self, item):
        if item in self._item_to_idx:
            return self._item_to_idx[item]
        else:
            raise TypeError('{} is not in list'.format(item))

    def __repr__(self):
        return repr(self._item_to_idx)

    def __str__(self):
        return str(self._item_to_idx)

if __name__ == '__main__':
    s = setlist([1, 2, 10, 3, 4, 3])
    print(s)
