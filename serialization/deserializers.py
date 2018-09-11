import json
from typing import Any, Dict, Generic, TypeVar

from tokenization import tokenizers

T = TypeVar('T')


class Deserializer(Generic[T]):
    @staticmethod
    def deserialize(s: str) -> T:
        raise NotImplementedError


class JsonDeserializer(Deserializer[T]):
    @staticmethod
    def from_json(j: dict) -> T:
        raise NotImplementedError

    @classmethod
    def deserialize(cls, s: str) -> T:
        return cls.from_json(json.loads(s))


# === Simple deserializers =================================================== #

class IdJsonDeserializer(JsonDeserializer[T]):
    @staticmethod
    def from_json(t: T) -> T:
        return t

class StrDeserializer(Deserializer[str]):
    @staticmethod
    def deserialize(s: str) -> str:
        return tokenizers.clean(s)


class SchemaJsonDeserializer(JsonDeserializer[Dict[str, Any]]):
    @property
    def schema(self) -> Dict:
        raise NotImplementedError

    @staticmethod
    def build(schema):
        SchemaJsonDeserializer.schema = schema
        return SchemaJsonDeserializer

    @staticmethod
    def _tokenize_json_list(json_obj: dict, field_spec):
        if type(field_spec) is list:
            if type(json_obj) is not list:
                raise TypeError
            result_spec = field_spec[0]
            return [SchemaJsonDeserializer._tokenize_json_list(e, result_spec)
                    for e in json_obj]
        if type(field_spec) is dict:
            if type(json_obj) is not dict:
                raise TypeError
            return SchemaJsonDeserializer._tokenize_json_dict(
                json_obj, field_spec)
        return field_spec(json_obj)

    @staticmethod
    def _tokenize_json_dict(json_obj: dict, schema: dict):
        result = {}
        for field_name, field_spec in schema.items():
            if field_name not in json_obj:
                continue
            contents = json_obj[field_name]
            if contents is None:
                continue
            if type(field_spec) is dict:
                if type(contents) is not dict:
                    raise TypeError
                result[field_name] = SchemaJsonDeserializer._tokenize_json_dict(
                    contents, field_spec)
            elif type(field_spec) is list:
                if type(contents) is not list:
                    raise TypeError
                result_spec = field_spec[0]
                result_list = [
                    SchemaJsonDeserializer._tokenize_json_list(e, result_spec)
                    for e in contents]
                result[field_name] = result_list
            else:
                result[field_name] = field_spec(contents)

        return result

    @staticmethod
    def from_json(j: dict) -> Dict[str, Any]:
        return SchemaJsonDeserializer._tokenize_json_dict(
            j, SchemaJsonDeserializer.schema)
