from serialization import JsonSerializer, JsonDeserializer
from tokenization import tokens


type_globals = vars(tokens)

class TokenSerializer(JsonSerializer[tokens.Token]):
    @staticmethod
    def to_json(t: tokens.Token):
        return {
            'type': t.__class__.__name__,
            'string': str(t)
        }


class TokenDeserializer(JsonDeserializer[tokens.Token]):
    @staticmethod
    def from_json(j: dict):
        assert isinstance(j['type'], str)
        assert isinstance(j['string'], str)
        cls = type_globals[j['type']]
        return cls(j['string'])
