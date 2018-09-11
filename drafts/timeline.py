import time
import tweepy

from dataio import get_twitter_auth
from dataio import TwitterConnSpecs

auth = get_twitter_auth(TwitterConnSpecs.from_json(
    {
        "access_token": "3327933191-DYOArYyktmW2AeLbaCeK3i6bw6Et4FK0Le5VP9R",
        "access_token_secret": "U91o13yf4mUNy5D1Q0F314m7L4bqtrLJ0F5saB7Tw5blE",
        "consumer_key": "zDz4ZHbei5X6o6jgMAcKNDWQy",
        "consumer_secret": "6HlyGwa0AaotbmMXLWzbQD8zoHax4BTu3mV9waFxt0OgaDc1E3"
    }
))

api = tweepy.API(auth)

user_ids = [('253270192', 966716370758127618)]

for user_id, max_id in user_ids:
    cache = {}
    tweet_count = 0
    with open('resources/pipeline/author_data/' + str(user_id) + '.json', 'w') as f:
        while tweet_count < 3200:
            while True:
                try:
                    print('Trying to get new timeline, max_id={}, so far we have {} tweets'.format(max_id, tweet_count))
                    timeline = api.user_timeline(user_id=user_id, count=200, max_id=max_id-1)
                    break
                except Exception as e:
                    print(str(e))
                    time.sleep(5)
            found = False
            tc = 0
            for tweet in timeline:
                tc += 1
                json = tweet._json
                tweet_id = int(json['id'])
                if tweet_id not in cache:
                    tweet_count += 1
                    print('Writing tweet #{} for user {}'.format(tweet_count, user_id))
                    f.write(str(json) + '\n')
                    cache[tweet_id] = 1
                    found = True
                max_id = min(max_id, tweet_id)
            if not found:
                print('No new tweets, received {} tweets and we had them all'.format(tc))
