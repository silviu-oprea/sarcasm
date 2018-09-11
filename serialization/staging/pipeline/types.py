from dataio import iotypes
from serialization import JsonSerializer, JsonDeserializer
from serialization.dataio.iotypes import NGramsSerializer, NGramsDeserializer
from staging.pipeline.types import User_Tweet, Example, Tweet


class User_TweetSerializer(JsonSerializer[User_Tweet]):
    @staticmethod
    def to_json(t: User_Tweet) -> dict:
        return {
            'uid': t.uid,
            'tid': t.tid
        }


class User_TweetDeserializer(JsonDeserializer[User_Tweet]):
    @staticmethod
    def from_json(j: dict) -> User_Tweet:
        assert isinstance(j['uid'], int)
        assert isinstance(j['tid'], int)
        return User_Tweet(j['uid'], j['tid'])


class ExampleSerializer(JsonSerializer[Example]):
    @staticmethod
    def to_json(t: Example) -> dict:
        return {
            'label': t.label,
            'point': TweetSerializer.to_json(t.point)
        }


class TweetSerializer(JsonSerializer[Tweet]):
    @staticmethod
    def to_json(t: Tweet) -> dict:
        obj = {
            'id': t.id,
            'uid': t.uid,
            'text': NGramsSerializer.to_json(t.text),
            'lang': t.lang,
            'truncated': t.truncated
        }
        if t.in_reply_to_status_id is not None:
            obj['in_reply_to_status_id'] = t.in_reply_to_status_id
        if t.in_reply_to_user_id is not None:
            obj['in_reply_to_user_id'] = t.in_reply_to_user_id
        if t.retweeted is not None:
            obj['retweeted'] = t.retweeted
        return obj


class TweetDeserializer(JsonDeserializer[Tweet]):
    @staticmethod
    def from_json(j: dict) -> Tweet:
        assert isinstance(j['id'], int)
        assert isinstance(j['uid'], int)
        assert isinstance(j['text'], dict)
        assert isinstance(j['lang'], str)
        assert isinstance(j['truncated'], bool)
        if 'in_reply_to_status_id' in j:
            assert isinstance(j['in_reply_to_status_id'], int)
        if 'in_reply_to_user_id' in j:
            assert isinstance(j['in_reply_to_user_id'], int)
        if 'retweeted' in j:
            assert isinstance(j['retweeted'], bool)
        return Tweet(j['id'], j['uid'], NGramsDeserializer.from_json(j['text']),
                     j['lang'], j['truncated'], j.get('in_reply_to_status_id'),
                     j.get('in_reply_to_user_id'), j.get('retweeted'))


class RawTweetDeserializer(JsonDeserializer[Tweet]):
    @staticmethod
    def from_json(j: dict) -> Tweet:
        assert isinstance(j['id'], int)
        assert isinstance(j['user'], dict)
        assert isinstance(j['user']['id'], int)
        assert isinstance(j['text'], str)
        assert isinstance(j['lang'], str)
        assert isinstance(j['truncated'], bool)
        if 'in_reply_to_status_id' in j:
            assert (j['in_reply_to_status_id'] is None or
                    isinstance(j['in_reply_to_status_id'], int))
        if 'in_reply_to_user_id' in j:
            assert (j['in_reply_to_user_id'] is None or
                    isinstance(j['in_reply_to_user_id'], int))
        retweeted = False
        if 'retweeted_status' in j:
            assert isinstance(j['retweeted_status'], dict)
            retweeted = True
        tweet = Tweet(j['id'], j['user']['id'], iotypes.SvNgrams(j['text']),
                      j['lang'], j['truncated'], j.get('in_reply_to_status_id'),
                      j.get('in_reply_to_user_id'), retweeted)
        return tweet


class ExampleDeserializer(JsonDeserializer[Example]):
    @staticmethod
    def from_json(j: dict):
        assert isinstance(j['label'], int)
        assert isinstance(j['point'], dict)
        return Example(TweetDeserializer.from_json(j['point']), j['label'])
