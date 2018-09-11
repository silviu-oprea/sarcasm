import logging
import os

from basic import log
from staging.pipeline import TwitterProvider

# Logging
logger = log.create_logger('main')
kfold_logger = log.create_logger('kfold', level=logging.INFO)
data_provider_logger = log.create_logger('data_provider', level=logging.INFO)

# Paths
root_path = '/Users/silviu/code/sarcasm/resources/data/real/tweets'
tweet_file_path = os.path.join(root_path, 'raw', 'twitter.json')

# Work
points, labels = TwitterProvider(tweet_file_path).data()

c = 0
for p, l in zip(points, labels):
    if l == 1:
        c += 1
print(c)
