from typing import Dict, TypeVar, Callable

KT = TypeVar('KT')
VT = TypeVar('VT')
VT1 = TypeVar('VT1')
VT2 = TypeVar('VT2')
VT3 = TypeVar('VT3')


def merge_dicts(d1: Dict[KT, VT1], d2: Dict[KT, VT2],
                merger: Callable[[VT1, VT2], VT3]) -> Dict[KT, VT3]:
    dm = d1.copy()
    for key, val in d2.items():
        if key in dm:
            dm[key] = merger(dm[key], val)
        else:
            dm[key] = val
    return dm


def map_values(f: Callable[[VT1], VT2], d: Dict[KT, VT1]) -> Dict[KT, VT2]:
    dm = {}
    for key in d:
        dm[key] = f(d[key])
    return dm
