import json
import typing as t

T = t.TypeVar('T')


class Serializer(t.Generic[T]):
    @classmethod
    def serialize(cls, t: T) -> str:
        raise NotImplementedError


class JsonSerializer(Serializer[T]):
    @staticmethod
    def to_json(t: T) -> dict:
        raise NotImplementedError

    @classmethod
    def serialize(cls, t: T) -> str:
        return json.dumps(cls.to_json(t))


class SvSerializer(Serializer[T]):
    @property
    def sep(self) -> str:
        raise NotImplementedError

    @staticmethod
    def to_sv(t: T) -> t.List:
        raise NotImplementedError

    @classmethod
    def serialize(cls, t: T):
        return cls.sep.join(cls.to_sv(t))


# === Simple serializers ===================================================== #

class IdSerializer(Serializer[T]):
    @classmethod
    def serialize(cls, t: T) -> str:
        return t

class IdJsonSerializer(JsonSerializer[dict]):
    @staticmethod
    def to_json(t: dict) -> dict:
        return t