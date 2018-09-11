from collections import defaultdict
from itertools import repeat
from typing import TypeVar, Sequence, Dict

T = TypeVar('T')


def frequency(smalls: Sequence[T], larges: Sequence[T]) -> Sequence[T]:
    res = list(repeat(0, len(larges)))
    for sitem in smalls:
        if sitem in larges:
            res[larges.index(sitem)] += 1
    return res


def histogram(seq: Sequence[T]) -> Dict[T, int]:
    hist = defaultdict(int)
    for item in seq:
        hist[item] += 1
    return hist


def indicators(smalls: Sequence[T], larges: Sequence[T]) -> Sequence[T]:
    res = list(repeat(0, len(larges)))
    for sitem in smalls:
        if sitem in larges:
            res[larges.index(sitem)] = 1
    return res
