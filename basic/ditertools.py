from collections import OrderedDict
from itertools import count, islice, repeat
from typing import (
    Callable, Iterable, Iterator, Mapping, Tuple, TypeVar, Sequence, DefaultDict)

from basic import functions
from basic.types import isiterable

T = TypeVar('T')
S = TypeVar('S')
KT = TypeVar('KT')
VT = TypeVar('VT')
VT_co = TypeVar('VT_co', covariant=True)


def chunks(csize: int, seq: Sequence[T]) -> Iterator[Sequence[T]]:
    for i in range(0, len(seq), csize):
        yield seq[i: i + csize]


def icount(f: Callable[[T], bool], iterable: Iterable[T]) -> int:
    count_ = 0
    for item in iterable:
        if f(item):
            count_ += 1
    return count_


def dedupe(key_extractor: Callable[[T], S],
           deduplicator: Callable[[T, T], T],
           iterable: Iterable[T]) -> Sequence[T]:
    cache = OrderedDict()
    for item in iterable:
        key = key_extractor(item)
        if key in cache:
            cache[key] = deduplicator(cache[key], item)
        else:
            cache[key] = item
    return cache.values()


def idiff(pos: Iterable[T], neg: Iterable[T]) -> Iterator[T]:
    for item in pos:
        if item not in neg:
            yield item


def filter_not(f: Callable[[T], bool], iterable: Iterable[T]) -> Iterator[T]:
    return filter(lambda x: not f(x), iterable)


def fold_left(f: Callable[[S, T], S], init: S, iterable: Iterable[T]) -> S:
    res = init
    for item in iterable:
        res = f(res, item)
    return res


def flatten(iterable: Iterable):
    for item in iterable:
        if isiterable(item):
            yield from flatten(item)
        else:
            yield item


def take(n: int, iterable: Iterable[T]) -> Iterator[T]:
    return islice(iterable, n)


def take_unique(n: int, key_extractor: Callable[[T], KT],
                iterable: Iterable[T]) -> Iterator[T]:
    return take(n, distinct(iterable, key_extractor))


def zip_with_index(iterable: Iterable[T]) -> Iterator[Tuple[T, int]]:
    return zip(iterable, count())


def reduce_left(f: Callable[[T, T], T], iterable: Iterable[T]) -> T:
    it = iter(iterable)
    res = next(it)
    for item in it:
        res = f(res, item)
    return res


def replicate(tpe: Callable[[], T], n: int) -> Iterator[T]:
    for _ in repeat(None, n):
        yield tpe()


class distinct(Iterator[T]):
    def __init__(self, iterable: Iterable[T], key_extractor: Callable[[T], S] = functions.id):
        self._it = iter(iterable)
        self._key_extractor = key_extractor
        self._visited = set()

    def __next__(self) -> T:
        item = next(self._it)
        key = self._key_extractor(item)
        while key in self._visited:
            item = next(self._it)
            key = self._key_extractor(item)
        self._visited.add(key)
        return item


class group_by(Mapping[KT, Sequence[VT]]):
    def __init__(self, keyx: Callable[[VT], KT], iterable: Iterable[VT]):
        groups = DefaultDict[KT, Sequence[VT]](list)
        for item in iterable:
            groups[keyx(item)].append(item)
        self._groups = groups

    def __getitem__(self, k: KT) -> VT:
        return self._groups[k]

    def __len__(self) -> int:
        return len(self._groups)

    def __iter__(self) -> Iterator[Tuple[KT, VT]]:
        return iter(self._groups.items())


def group_indices_by(key_extractor: Callable[[T], KT], iterable: Iterable[T]
                     ) -> Mapping[KT, Sequence[int]]:
    groups = DefaultDict[KT, Sequence[int]](list)
    for idx, item in enumerate(iterable):
        groups[key_extractor(item)].append(idx)
    return groups


def split(f: Callable[[T], Tuple[T, T]], iterable: Iterable[T]) -> Tuple[Sequence[T], Sequence]:
    leftc = list()
    rightc = list()
    for item in iterable:
        left, right = f(item)
        leftc.append(left)
        rightc.append(right)
    return leftc, rightc


def get_all(idxs: Iterable[T], seq: Sequence[T]) -> Sequence[T]:
    return [seq[idx] for idx in idxs]


if __name__ == '__main__':
    l1 = [('a', 4), ('b', 4), ('a', 7), ('c', 10)]
    d = dedupe(lambda t: t[0], lambda t1, t2: t1 if t1[1] > t2[1] else t2, l1)
    print(d)