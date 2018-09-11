import logging
from typing import Generic, Iterator, Type, TypeVar, Iterable, Tuple

from serialization import Deserializer
from serialization.serializers import Serializer
from basic import filesystem

T = TypeVar('T')
logger = logging.getLogger('dataio.fileio.accessors')


class FileAccessor:
    def __init__(self, path, mode: str, encoding: str):
        filesystem.ensure_writable_file_loc(path)
        self._fp = open(path, mode, encoding=encoding)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._fp.close()


class FileDumpers:
    def __init__(self, name_path: Iterable[Tuple],
                 serializer: Type[Serializer[T]],
                 mode: str = 'a', encoding: str = 'utf-8'):
        dumpers = map(
            lambda np: (np[0], FileDumper(str(np[1]), serializer, mode, encoding)),
            name_path)
        self._dumpers = dict(dumpers)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for _, dumper in self._dumpers.items():
            dumper.__exit__(exc_type, exc_value, traceback)

    def __getitem__(self, key):
        return self._dumpers[key]


class FileDumper(FileAccessor, Generic[T]):
    def __init__(self, path: str, serializer: Type[Serializer[T]],
                 mode: str = 'a', encoding: str = 'utf-8'):
        self._serializer = serializer
        super().__init__(path, mode, encoding)

    def dump(self, t: T):
        self._fp.write(self._serializer.serialize(t))
        self._fp.write('\n')

    def dump_all(self, ts: Iterator[T]):
        for t in ts:
            self.dump(t)


class FileLoader(FileAccessor, Iterator[T]):
    def __init__(self, path: str, deserializer: Type[Deserializer[T]],
                 mode: str = 'r', encoding: str = 'utf-8'):
        self._deserializer = deserializer
        super().__init__(path, mode, encoding)

    def __next__(self):
        while True:
            try:
                line = next(self._fp)
                return self._deserializer.deserialize(line)
            except TypeError as e:
                logger.info('[FileLoader] cannot deserialize {}: {}'
                            .format(line[:30], e))

    def skip(self):
        next(self._fp)

    def load_all(self):
        contents = self._fp.read()
        return self._deserializer.deserialize(contents)
