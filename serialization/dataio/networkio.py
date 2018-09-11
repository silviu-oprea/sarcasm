from dataio.networkio import TwitterConnSpecs
from serialization import JsonDeserializer


class TwitterConnSpecsDeserializer(JsonDeserializer):
    @staticmethod
    def from_json(jd: dict) -> TwitterConnSpecs:
        return TwitterConnSpecs(jd['access_token'],
                                jd['access_token_secret'],
                                jd['consumer_key'],
                                jd['consumer_secret'])
