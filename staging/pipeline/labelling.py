import logging
import numpy as np
import os
from collections import defaultdict

from basic import filesystem, functions
from basic.ditertools import filter_not, split, idiff, take
from basic.stattools import histogram
from dataio import fileio, iotypes, iopipes
from ml.feature_extractors.feature_extractor import FeatureExtractor
from serialization.staging.pipeline.stats import (
    HstStatSerializer, TopicsStatSerializer, HstStatDeserializer,
    TopicsStatDeserializer)
from serialization.staging.pipeline.types import RawTweetDeserializer, ExampleSerializer, ExampleDeserializer
from staging.pipeline.stats import (
    VocabularyStatBuilder, HstStatBuilder, TopicsStatBuilder, AllStats)
from staging.pipeline.types import Tweet, Example
from tokenization import tokens

logger = logging.getLogger('labelling')
label_space = [0, 1]


def add_label(tweet: Tweet) -> Example:
    is_reply = tweet.in_reply_to_status_id is not None
    is_not_retweet = tweet.retweeted is False
    allowed_tail_tokens = [tokens.HashtagToken('#sarcasm'),
                           tokens.HashtagToken('#sarcastic')]
    sarcastic_text = lambda: tweet.text.has_valid_tail(
        allowed_tail_tokens, case_sensitive=False)
    #label = int(is_reply and is_not_retweet and sarcastic_text())
    import random
    label = random.getrandbits(1)
    filtered_text = filter_not(
        lambda token: any(token.eq(allowed_token, case_sensitive=False)
                          for allowed_token in allowed_tail_tokens),
        tweet.text)
    tweet.text = iotypes.NGrams(list(filtered_text))
    return Example(tweet, label)


def valid_tweet(tweet: Tweet):
    return tweet.lang == 'en' and len(tweet.text) > 3


def gen_examples_and_vocab(user_raw_dir_in: str, user_labelled_dir_out: str,
                           stats_dir_out: str,  min_ex_per_user: int):

    vocab_file = os.path.join(stats_dir_out, 'vocabulary.txt')
    prev_vocab = []
    if filesystem.readable_file(vocab_file):
        prev_vocab = iopipes.Pipe.from_path(vocab_file)
    vocab = VocabularyStatBuilder(prev_vocab)

    for path, u_tweet_it in iopipes.Pipe.named_from_path(
            user_raw_dir_in, RawTweetDeserializer, min_ex_per_user):
        uid = int(filesystem.name(path))
        u_ex_it = map(add_label, filter(valid_tweet, u_tweet_it))

        path_root = os.path.join(user_labelled_dir_out, str(uid))
        ex_files_out = list(map(
            lambda label: os.path.join(path_root, str(label) + '.json'),
            label_space))
        if not filesystem.readable_files(*ex_files_out):
            logger.info('[generate_examples_and_vocab] '
                        'Generating examples for user {}'.format(uid))
            with fileio.FileDumpers(zip(label_space, ex_files_out),
                                    ExampleSerializer,
                                    mode=fileio.WriteModes.WRITE) as dumpers:
                hst, topics = HstStatBuilder(uid), TopicsStatBuilder(uid)
                labels_hist = defaultdict(int)
                for ex in u_ex_it:
                    hst.add(ex)
                    topics.add(ex)
                    vocab.add(ex)
                    dumpers[ex.label].dump(ex)
                    labels_hist[ex.label] += 1
                logger.info('[generate_examples_and_stats] Done generating '
                            'examples for user {}. Label class balance: {}'
                            .format(uid, labels_hist))

    logger.info('[generate_examples_and_stats] Done')
    fileio.it_to_file(vocab.get(), vocab_file, mode=fileio.WriteModes.WRITE)


def get_examples(users_labelled_dir_in: str, main_class: int, class_ratio: float):
    assert 0 <= class_ratio <= 1, 'pos_neg_ratio should be between 0 and 1'
    logger.info('[get_examples] Reading examples from ' + users_labelled_dir_in)

    users_labelled_dir_obj = iopipes.Pipe\
        .recursive_from_path(users_labelled_dir_in, ExampleDeserializer)

    points = []
    labels = []
    for uid, dir_obj in users_labelled_dir_obj.items():
        for main_ex in dir_obj.file(str(main_class)):
            points.append(main_ex.point)
            labels.append(main_ex.label)
        nr_other_ex = int((1/class_ratio) * len(points))
        for other_class in idiff(pos=label_space, neg=[main_class]):
            for other_ex in take(nr_other_ex, dir_obj.file(str(other_class))):
                points.append(other_ex.point)
                labels.append(other_ex.label)
    logger.info('[get_examples] Done reading examples. Class distribution: {}'
                .format(histogram(labels)))

    return points, labels


def get_vocab(stats_dir_in: str):
    vocab_file_in = os.path.join(stats_dir_in, 'vocabulary.txt')
    logger.info('[get_vocab] Reading vocab from ' + vocab_file_in)
    return list(iopipes.Pipe.from_path(vocab_file_in))


def get_stats(stats_dir_in: str):
    """
    :param stats_dir_in: path to a directory with structure
           stats_dir_in/[hst.json, topics.json]
    """
    hst_file_in = os.path.join(stats_dir_in, 'hst.json')
    topics_file_in = os.path.join(stats_dir_in, 'topics.json')
    vocab_file_in = os.path.join(stats_dir_in, 'vocabulary.txt')

    logger.info('[get_examples] Reading stats:'
                '\n\thst from {}'
                '\n\ttopics from {}'
                '\n\tvocab fromm {}'
                .format(hst_file_in, topics_file_in, vocab_file_in))

    hst = dict(iopipes.Pipe.from_path(hst_file_in, HstStatDeserializer))
    topics = dict(iopipes.Pipe.from_path(topics_file_in, TopicsStatDeserializer))
    vocab = list(iopipes.Pipe.from_path(vocab_file_in))
    return AllStats(vocab, hst, topics)

