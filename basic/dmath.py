import math

from basic import functions
from basic.ditertools import reduce_left


def euclidean_distance(lst1, lst2, normalized=False):
    assert len(lst1) == len(lst2)
    if normalized:
        lst1 = normalize(lst1)
        lst2 = normalize(lst2)
    squared_dist = reduce_left(
        functions.add2,
        map(lambda xy: functions.sqr(xy[0] - xy[1]),
            zip(lst1, lst2)))
    dist = math.sqrt(squared_dist)
    return dist


def compute_norm(lst):
    norm = math.sqrt(reduce_left(functions.add2, map(functions.sqr, lst)))
    return norm


def normalize(lst):
    norm = compute_norm(lst)
    lst_normalized = map(lambda x: x / norm, lst)
    return lst_normalized


if __name__ == '__main__':
    l1 = [1, 2, 3]
    l2 = [1, 12, 9]
    print(euclidean_distance(l1, l2))
