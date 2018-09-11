from typing import Iterator

from dataio.fileio import accessors
from serialization.serializers import IdSerializer


class WriteModes:
    WRITE = 'w'
    APPEND = 'a'


def it_to_file(it: Iterator, path: str,
               serializer=IdSerializer, mode='a', encoding='utf-8'):
    with accessors.FileDumper(path, serializer, mode, encoding) as fd:
        fd.dump_all(it)
