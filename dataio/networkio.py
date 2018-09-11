import logging
import time
from typing import Iterator, Iterable, List, Sequence

import tweepy
import queue
from tweepy import OAuthHandler

import basic
from basic.ditertools import chunks

logger = logging.getLogger('network_provider')


class TwitterConnSpecs(basic.types.Printable):
    def __init__(self, access_token,
                 access_token_secret, consumer_key, consumer_secret):
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret


class TwitterListener(tweepy.streaming.StreamListener):
    def __init__(self):
        super().__init__()
        self.q = queue.Queue()

    def generator(self):
        while True:
            try:
                value = self.q.get()
            except StopIteration:
                return
            yield value

    def on_data(self, data):
        self.q.put(data)

    def on_error(self, status):
        print('WARN:' + str(status))


def get_twitter_auth(twitter_conn_specs: TwitterConnSpecs) -> OAuthHandler:
    auth = tweepy.OAuthHandler(
        twitter_conn_specs.consumer_key,
        twitter_conn_specs.consumer_secret)
    auth.set_access_token(
        twitter_conn_specs.access_token,
        twitter_conn_specs.access_token_secret)
    return auth


def get_tweet_it(twitter_conn_spec: TwitterConnSpecs,
                 filter_words: Iterable[str]
                 ) -> Iterator:
    listener = TwitterListener()
    auth = get_twitter_auth(twitter_conn_spec)
    stream = tweepy.Stream(auth, listener)
    stream.filter(track=filter_words, async=True)
    return listener.generator()


def get_timeline_it(twitter_conn_spec: TwitterConnSpecs,
                    user_id: int, how_many: int) -> Iterator:
    auth = get_twitter_auth(twitter_conn_spec)
    api = tweepy.API(auth)
    user_timeline = api.user_timeline(user_id=user_id, count=how_many)
    for post in user_timeline:
        yield post._json


def lookup_100_users(user_ids: Sequence[int], twitter_auth: OAuthHandler):
    api = tweepy.API(twitter_auth)
    while True:
        try:
            return api.lookup_users(user_ids)
        except Exception as e:
            logger.info('[lookup_100_users] This happened: {}. Trying again'
                        .format(str(e)))


def lookup_users(user_ids: Sequence[int], twitter_auth: OAuthHandler) -> Sequence:
    logger.info('[lookup_users] Need to look up {} users'.format(len(user_ids)))

    left = len(user_ids)
    users = []
    for chunk in chunks(100, user_ids):
        logger.info('[lookup_users] {} left, looking up 100 more'.format(left))
        chunk_users = lookup_100_users(chunk, twitter_auth)
        users.extend(chunk_users)
        left -= 100
    return list(map(lambda obj: obj._json, users))


def get_active_uids(user_ids, twitter_auth) -> Sequence:
    return list(map(lambda obj: obj['id'],
                    lookup_users(user_ids, twitter_auth)))


class TweetTimelineProvider:
    api = None

    def __init__(self, twitter_auth, user_id: int, max_tweet_id: int):
        super().__init__()
        self._count = 0
        self._user_id = user_id
        self._timeline_it = iter(())
        self._max_tweet_id = max_tweet_id
        self._last_max_tweet_id = None
        if TweetTimelineProvider.api is None:
            logger.info('[TweetTimelineProvider] Initializing api')
            TweetTimelineProvider.api = tweepy.API(twitter_auth)

    def _get_new_timeline(self, max_tweet_id):
        attempt_count = 1
        sleep_time = 2
        while True:
            try:
                time.sleep(0.5)
                logger.info('[TweetTimelineProvider] Requesting new timeline of 200 tweets with max id {} '
                            'for user {} '
                            '(attempt {})'
                            .format(max_tweet_id, self._user_id, attempt_count))
                timeline = TweetTimelineProvider.api.user_timeline(user_id=self._user_id,
                                                                   count=200,
                                                                   max_id=max_tweet_id)
                break
            except BaseException as e:
                logger.info('[TweetTimelineProvider] Failed with message "{}". Retrying in {} sec'
                            .format(str(e), sleep_time))
                if attempt_count > 9:
                    raise StopIteration
                time.sleep(sleep_time)
                attempt_count += 1
                sleep_time *= 2
        self._timeline_it = iter(timeline)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            tweet = next(self._timeline_it)
        except StopIteration:
            if self._max_tweet_id == self._last_max_tweet_id:
                raise StopIteration
            self._get_new_timeline(self._max_tweet_id)
            tweet = next(self._timeline_it)
        self._count += 1
        if self._count % 1000 == 0:
            logger.info('[TweetTimelineProvider] Providing tweet #{} for user id {}'
                        .format(self._count, self._user_id))
        tweet_json = tweet._json
        tweet_id = int(tweet_json['id'])
        self._last_max_tweet_id = self._max_tweet_id
        self._max_tweet_id = min(self._max_tweet_id, tweet_id)
        return tweet_json


if __name__ == '__main__':
    auth = get_twitter_auth(TwitterConnSpecs(
            access_token = "3327933191-DYOArYyktmW2AeLbaCeK3i6bw6Et4FK0Le5VP9R",
            access_token_secret = "U91o13yf4mUNy5D1Q0F314m7L4bqtrLJ0F5saB7Tw5blE",
            consumer_key = "zDz4ZHbei5X6o6jgMAcKNDWQy",
            consumer_secret = "6HlyGwa0AaotbmMXLWzbQD8zoHax4BTu3mV9waFxt0OgaDc1E3"
    ))
    api = tweepy.API(auth)
    # print(api.rate_limit_status())
    # lookup_users(List([253270192, 966716113060028420]), auth)
    t = api.user_timeline(user_id=253270192, count=10, max_id=38000890929618944)
    for tweet in t:
        print(tweet._json['id'])