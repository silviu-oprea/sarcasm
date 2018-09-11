import logging
from typing import Any, Dict, Iterator, Tuple, Type, TypeVar

from dataio import fileio, networkio
from serialization import StrDeserializer, Deserializer

T = TypeVar('T')
logger = logging.getLogger('dataio.iopipes')


class Pipe:
    @staticmethod
    def twitter_user_timeline(twitter_auth, user_id: int, max_tweet_id: int
                              ) -> Iterator:
        return networkio.TweetTimelineProvider(
            twitter_auth, user_id, max_tweet_id)

    @staticmethod
    def from_path(path: str,
                  deserializer: Type[Deserializer[T]] = StrDeserializer,
                  min_lines: int = 1, skip_header: bool = False,
                  recursive: bool = True,
                  ) -> Iterator[T]:
        return fileio.path_to_line_it(
            path, min_lines, skip_header, recursive, deserializer)

    @staticmethod
    def named_from_path(path: str,
                        deserializer: Type[Deserializer[T]] = StrDeserializer,
                        min_lines: int = 1, skip_header: bool = False,
                        recursive: bool = True,
                        ) -> Iterator[Tuple[str, Iterator[T]]]:
        return fileio.path_to_named_line_it(
            path, min_lines, skip_header, recursive, deserializer)

    @staticmethod
    def recursive_from_path(path,
                            deserializer: Type[Deserializer[T]] = StrDeserializer,
                            min_lines: int = 1, skip_header: bool = False,
                            ) -> 'RecursivePipingProvider':
        path_dict = fileio.dir_to_recursive_named_line_it(
            path, min_lines, skip_header, deserializer)
        return RecursivePipingProvider(path_dict)


class RecursivePipingProvider:
    def __init__(self, path_dict: Dict[str, Any]):
        self._path_dict = path_dict

    def file(self, name: str) -> Iterator:
        assert isinstance(self._path_dict[name], Iterator)
        return self._path_dict[name]

    def dir(self, name: str) -> Dict[str, Any]:
        assert isinstance(self._path_dict[name], Dict[str, Any])
        return self._path_dict[name]

    def items(self):
        for key, val in self._path_dict.items():
            if isinstance(self._path_dict[key], Iterator):
                yield key, self._path_dict[key]
            else:
                yield key, RecursivePipingProvider(self._path_dict[key])
