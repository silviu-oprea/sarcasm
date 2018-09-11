from ml.kfold import KFoldIndices
from serialization import JsonSerializer, JsonDeserializer


class KFoldIndicesSerializer(JsonSerializer):
    @staticmethod
    def to_json(obj) -> dict:
        return {
            'train': obj.train,
            'valid': obj.valid,
            'test': obj.test
        }


class KFoldIndicesDeserializer(JsonDeserializer):
    @staticmethod
    def from_json(j: dict) -> KFoldIndices:
        assert isinstance(j['train'], list)
        assert isinstance(j['valid'], list)
        assert isinstance(j['test'], list)
        return KFoldIndices(j['train'], j['valid'], j['test'])
