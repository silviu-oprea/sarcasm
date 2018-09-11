import glob
import logging
from itertools import takewhile, repeat
from typing import Any, Type, NamedTuple, TypeVar, Iterator, Iterable, Dict

from dataio.fileio import accessors
from serialization import Deserializer, StrDeserializer
from basic import filesystem

T = TypeVar('T')
logger = logging.getLogger('dataio.fileio.readers')


def count_lines(path: str, skip_header: bool = False) -> int:
    f = open(path, 'rb')
    buf_gen = takewhile(lambda x:
                        x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
    line_count = sum(buf.count(b'\n') for buf in buf_gen)
    if skip_header:
        line_count -= 1
    f.close()
    return line_count


def file_to_type(path, deserializer: Type[Deserializer[T]] = StrDeserializer,
                 skip_header=False) -> T:
    with accessors.FileLoader(path, deserializer) as f:
        if skip_header:
            f.skip()
        return f.load_all()


def file_to_line_it(path, skip_header: bool = False,
                    deserializer: Type[Deserializer[T]] = StrDeserializer
                    ) -> Iterator[T]:
    linum = 0
    with accessors.FileLoader(path, deserializer) as f:
        if skip_header:
            f.skip()
            linum += 1
        for line in f:
            linum += 1
            logger.info('[file_to_line_it] Loading line {} from {}'
                        .format(linum, path))
            yield line


# Access mode 1: Iterator[Line], over all lines from all files
def multifile_to_line_it(paths: Iterable[str], min_lines: int,
                         skip_header: bool = False,
                         deserializer: Type[Deserializer[T]] = StrDeserializer
                         ) -> Iterator[T]:
    valid_paths = filter(lambda p: count_lines(p, skip_header) >= min_lines,
                         paths)
    for path in valid_paths:
        for line in file_to_line_it(path, skip_header, deserializer):
            yield line


def dir_to_line_it(path: str, min_lines: int,
                   skip_header: bool = False, recursive: bool = True,
                   deserializer: Type[Deserializer[T]] = StrDeserializer
                   ) -> Iterator[T]:
    if recursive:
        path = path + '/**/*.*'
    else:
        path = path + '/*.*'
    paths = glob.glob(path, recursive=recursive)
    return multifile_to_line_it(paths,
                                min_lines, skip_header, deserializer)


def path_to_line_it(path: str, min_lines: int,
                    skip_header: bool = False, recursive: bool = True,
                    deserializer: Type[Deserializer[T]] = StrDeserializer
                    ) -> Iterator[T]:
    if filesystem.readable_dir(path):
        return dir_to_line_it(path, min_lines, skip_header, recursive,
                              deserializer)
    else:
        return multifile_to_line_it([path],
                                    min_lines, skip_header, deserializer)


# Access mode 2: Iterator[Tuple[<full file path>, Iterator[Line]]]
# where <full file path> is the full path to the file, relative to <root>.
# So, for instance, if we have the file structure:
# /a/b/f1.txt
# /a/c/f2.txt
# /a/f3.txt
# we will have Iterator[
#     (/a/b/f1.txt, Iterator[f1.txt lines]),
#     (/a/c/f2.txt, Iterator[f2.txt lines]),
#     (/a/f3.txt,   Iterator[f3.txt lines]]
class Path_It(NamedTuple):
    path: str
    it: Iterator[T]


def multifile_to_named_line_it(paths: Iterable[str], min_lines: int,
                               skip_header: bool = False,
                               deserializer: Type[Deserializer[T]] = StrDeserializer
                               ) -> Iterator[Path_It]:

    valid_paths = filter(lambda p: count_lines(p, skip_header) >= min_lines,
                         paths)
    for path in valid_paths:
        yield Path_It(path, file_to_line_it(path, skip_header, deserializer))


def dir_to_named_line_it(path: str, min_lines: int,
                         skip_header: bool = False, recursive: bool = True,
                         deserializer: Type[Deserializer[T]] = StrDeserializer
                         ) -> Iterator[Path_It]:
    if recursive:
        path = path + '/**/*.*'
    else:
        path = path + '/*.*'
    paths = glob.glob(path, recursive=recursive)
    return multifile_to_named_line_it(paths,
                                      min_lines, skip_header, deserializer)


def path_to_named_line_it(path: str, min_lines: int,
                          skip_header: bool = False, recursive: bool = False,
                          deserializer: Type[Deserializer[T]] = StrDeserializer
                          ) -> Iterator[Path_It]:
    if filesystem.readable_dir(path):
        return dir_to_named_line_it(
            path, min_lines, skip_header, recursive, deserializer)
    else:
        return multifile_to_named_line_it(
            [path], min_lines, skip_header, deserializer)


# Access mode 3: Iterator[Tuple[<file/dir name>, Iterator[Line/?]]]
# where <file/dir path> is the name of the current file/dir.
# So, for instance, if we have the file structure:
# /a/b/f1.txt
# /a/b/f2.txt
# /a/c/f3.txt
# /d/f4.txt
# /a/f5.txt
# we will have Iterator[
#     (/a, Iterator[
#         (/b, Iterator[(f1.txt, Iterator[f1.txt lines]),
#                       (f2.txt, Iterator[f2.txt lines])]),
#         (/c, Iterator[(f3.txt, Iterator[f3.txt lines])]),
#         (f5.txt, Iterator[f5.txt lines])
#     ]),
#     (/d, Iterator[(f4.txt, Iterator[f3.txt lines])])
# ])
#     (/a/b/f1.txt, Iterator[f1.txt lines]),
#     (/a/c/f2.txt, Iterator[f2.txt lines]),
#     (/a/f3.txt,   Iterator[f3.txt lines]]
def dir_to_recursive_named_line_it(
        path: str, min_lines: int, skip_header: bool = False,
        deserializer: Type[Deserializer[T]] = StrDeserializer
        ) -> Dict[str, Any]:
    assert filesystem.readable_dir(path), path + ' is not a directory'

    res = {}
    for member_path in glob.glob(path + '/*'):
        name = filesystem.name(member_path)
        if filesystem.readable_file(member_path):
            res[name] = multifile_to_line_it(
                [member_path], min_lines, skip_header, deserializer)
        else:
            res[name] = dir_to_recursive_named_line_it(
                member_path, min_lines, skip_header, deserializer)
    return res
