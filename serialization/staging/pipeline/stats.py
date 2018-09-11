from basic.dcollections import setlist
from serialization import JsonSerializer, JsonDeserializer
from staging.pipeline.stats import HstStat, TopicsStat


class HstStatSerializer(JsonSerializer[HstStat]):
    @staticmethod
    def to_json(t: HstStat) -> dict:
        return {
            'uid': t.uid,
            'hst': t.hst
        }


class HstStatDeserializer(JsonDeserializer[HstStat]):
    @staticmethod
    def from_json(j: dict) -> HstStat:
        assert isinstance(j['uid'], int)
        assert isinstance(j['hst'], list)
        hst = setlist(j['hst'])
        return HstStat(j['uid'], hst)


class TopicsStatSerializer(JsonSerializer[TopicsStat]):
    @staticmethod
    def to_json(t: TopicsStat) -> dict:
        return {
            'uid': t.uid,
            'topics': t.topics
        }


class TopicsStatDeserializer(JsonDeserializer[TopicsStat]):
    @staticmethod
    def from_json(j: dict) -> TopicsStat:
        assert isinstance(j['uid'], int)
        assert isinstance(j['topics'], list)
        return TopicsStat(j['uid'], j['topics'])
