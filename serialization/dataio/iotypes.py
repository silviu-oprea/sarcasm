from dataio import iotypes
from serialization import JsonSerializer, JsonDeserializer
from serialization.tokenization.tokens import TokenSerializer, TokenDeserializer


class NGramsSerializer(JsonSerializer[iotypes.NGrams]):
    @staticmethod
    def to_json(t: iotypes.NGrams) -> dict:
        return {
            'unigrams': [TokenSerializer.to_json(u) for u in t]
        }


class NGramsDeserializer(JsonDeserializer[iotypes.NGrams]):
    @staticmethod
    def from_json(j: dict) -> iotypes.NGrams:
        assert isinstance(j['unigrams'], list)
        unigrams = [TokenDeserializer.from_json(ij) for ij in j['unigrams']]
        return iotypes.NGrams(unigrams)
