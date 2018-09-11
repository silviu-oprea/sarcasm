from itertools import groupby
from typing import TypeVar, List, Iterator

T = TypeVar('T')


class MyList(Iterator):
    def __init__(self):
        self.lst = [1, 2, 2, 3]
        self.idx = 0

    def __next__(self):
        if self.idx >= len(self.lst):
            raise StopIteration
        #print('next called')
        item = self.lst[self.idx]
        self.idx += 1
        return item
