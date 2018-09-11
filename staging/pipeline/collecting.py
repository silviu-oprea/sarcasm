import logging
import os
from typing import Iterator

from basic import filesystem
from basic.ditertools import dedupe, take_unique
from dataio import networkio, fileio, iopipes
from serialization import IdJsonSerializer, SchemaJsonDeserializer
from serialization.staging.pipeline.types import (
    User_TweetDeserializer, User_TweetSerializer)
from staging.pipeline.types import User_Tweet

logger = logging.getLogger('collecting')


def get_active_uts(uts, twitter_auth):
    active_uids = networkio.get_active_uids(
        list(map(lambda ut: ut.uid, uts)), twitter_auth)
    active_uids = set(active_uids)
    return list(filter(lambda ut: ut.uid in active_uids, uts))


def get_active_seed_uids(seed_file_in, twitter_auth
                         ) -> Iterator[User_Tweet]:
    active_uts_file = filesystem.remove_ext(seed_file_in) + '_active.txt'

    if filesystem.readable_file(active_uts_file):
        logger.info('[get_active_seed_uids] Reading (active user id, '
                    'latest tweet id) pairs from {}'.format(active_uts_file))
        return list(
            iopipes.Pipe.from_path(active_uts_file, User_TweetDeserializer))

    logger.info('[get_active_seed_uids] Generating (active user ids, '
                'latest tweets id) pairs into {}'.format(active_uts_file))
    uts = iopipes.Pipe.from_path(
        seed_file_in,
        SchemaJsonDeserializer.build(
            {'id': int, 'user': {'id': int}, 'lang': str}))
    uts = filter(lambda d: d['lang'] == 'en', uts)
    uts = map(lambda d: User_Tweet(d['user']['id'], d['id']), uts)
    uts = dedupe(lambda ut: ut.uid,
                 lambda ut1, ut2: ut1 if ut1.tid > ut2.tid else ut2,
                 uts)
    active_uts = get_active_uts(uts, twitter_auth)
    fileio.it_to_file(active_uts, active_uts_file, User_TweetSerializer)
    return active_uts


def collect_user_hist_tweets(active_uts, user_raw_dir_out,
                             nr_tweets_per_user, twitter_auth):
    logger.info('[collect_user_hist_tweets] Got {} users active user ids'
                .format(len(active_uts)))
    for idx, (uid, tid) in enumerate(active_uts, start=1):
        user_file_out = os.path.join(user_raw_dir_out, str(uid) + '.json')
        if not filesystem.readable_file(user_file_out):
            logger.info('[collect_user_hist_tweets] Retrieving tweets for {} '
                        '[user {} / {}]'
                        .format(uid, idx, len(active_uts)))
            it = iopipes.Pipe.twitter_user_timeline(twitter_auth, uid, tid)
            it = take_unique(nr_tweets_per_user,
                             lambda json_obj: json_obj['id'],
                             it)
            fileio.it_to_file(it, user_file_out, IdJsonSerializer)
