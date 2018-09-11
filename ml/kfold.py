import logging
from collections import namedtuple
from itertools import repeat
from typing import Sequence, Iterator

import numpy as np

from basic import dmath, functions
from basic.dcollections import setlist
from basic.ditertools import replicate, group_indices_by, distinct, reduce_left, flatten, get_all
from basic.stattools import frequency

logger = logging.getLogger('ml.kfold')

KFoldIndices = namedtuple(
    'KFoldIndices', ['train', 'valid', 'test'], verbose=False)


class SplitSpec:
    def __init__(self, train: float, valid: float, test: float):
        assert 0 <= train <= 1 and \
               0 <= test <= 1 and \
               0 <= valid <= 1 and \
               train + test + valid == 1
        self.train = train
        self.valid = valid
        self.test = test


class KFold:
    def __init__(self, k: int):
        self._k = k

    def _split(self, points: Sequence, labels: Sequence, split_spec: SplitSpec
               ) -> Iterator[KFoldIndices]:
        raise NotImplementedError

    def split(self, points: Sequence, labels: Sequence, split_spec: SplitSpec
              ) -> Iterator[KFoldIndices]:
        return self._split(points, labels, split_spec)


class CircularIndexIterator:
    def __init__(self, n):
        self._n = n
        self._start = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._start < self._n:
            lst = [(self._start + d) % self._n for d in range(self._n)]
            self._start += 1
            return lst
        else:
            raise StopIteration()


class GroupedKFold(KFold):
    def __init__(self, k, key_extractor):
        super().__init__(k)
        self._key_extractor = key_extractor

    def _dist(self, group, bucket, labels, distinct_labels, max_bucket_len):
        if len(bucket) == 0:
            return 0

        group_labels = list(labels[idx] for idx in group)
        bucket_labels = list(labels[idx] for idx in bucket)

        # Distribution of bucket labels over the space of all possible labels
        bucket_label_distr = frequency(bucket_labels, distinct_labels)
        # Given the same total mass, how would the uniform distribution would
        # look like. That is, a perfect class balance (eg. same amount of
        # positive and negative examples)
        bucket_total_mass = reduce_left(functions.add2, bucket_label_distr)
        bucket_uniform_value = bucket_total_mass / len(distinct_labels)
        bucket_uniform_distr = list(repeat(bucket_uniform_value, len(distinct_labels)))
        # Distance between the actual bucket distribution and the bucket
        # distribution. Since the vectors are normalized,
        # ||x-y|| <= ||x|| + ||y|| = 2, by triangle inequality. We divide by 2
        # to get a number between 0 and 1.
        bucket_only_imbalance = dmath.euclidean_distance(
            bucket_label_distr, bucket_uniform_distr, normalized=True) / 2

        # Same calculations for the scenario of adding this group to this bucket
        group_label_distr = frequency(group_labels, distinct_labels)
        joint_label_distr = list(map(functions.add2t,
                                     zip(group_label_distr, bucket_label_distr)))
        joint_total_mass = reduce_left(lambda x, y: x + y, joint_label_distr)
        joint_uniform_value = joint_total_mass / len(distinct_labels)
        joint_uniform_distr = list(repeat(joint_uniform_value, len(joint_label_distr)))
        joint_imbalance = dmath.euclidean_distance(
            joint_label_distr, joint_uniform_distr, normalized=True) / 2

        # bucket_only_imbalance - joint_imbalance \in [-1, 1].
        # Divide by 2 and add 0.5 to scale to [0, 1].
        # Do 1 - result, so that largest improvements come first
        # in the ascending sorting.
        dist_improvement = 1 \
                           - ((bucket_only_imbalance - joint_imbalance) / 2
                              + 0.5)
        norm_bucket_len = len(bucket) / max_bucket_len

        dist_importance = 0.5
        bucket_len_importance = 0.5
        return bucket_len_importance * norm_bucket_len \
               + dist_importance * dist_improvement

    def _split(self, points: Sequence, labels: Sequence, split_spec: SplitSpec
               ) -> Iterator[KFoldIndices]:
        valid_start = round(self._k * split_spec.train)
        test_start = round(valid_start + self._k * split_spec.valid)

        train_size = valid_start
        valid_size = test_start - valid_start
        test_size = self._k - test_start

        assert train_size > 0 and valid_size > 0 and test_size > 0

        buckets = list(replicate(list, self._k))
        key_to_group = sorted(
            group_indices_by(self._key_extractor, points).items(),
            key=lambda k0_g1: len(k0_g1[1]), reverse=True
        )
        logger.info('[GroupedKFold._split] Splitting points into buckets')
        distinct_labels = setlist(distinct(labels))

        for key, group in key_to_group:
            target_bucket = min(
                buckets,
                key=lambda bucket: self._dist(
                    group, bucket, labels, distinct_labels, len(points)))
            target_bucket.extend(group)

        log_msg = '[GroupedKFold._split] Split into {} groups of sizes {}'.format(
            self._k,
            [len(v) for v in buckets])
        logger.info(log_msg)

        for split in CircularIndexIterator(self._k):
            train_bucket_idx = split[0: valid_start]
            valid_bucket_idx = split[valid_start: test_start]
            test_bucket_idx = split[test_start:]

            train_idx = list(flatten(get_all(train_bucket_idx, buckets)))
            valid_idx = list(flatten(get_all(valid_bucket_idx, buckets)))
            test_idx = list(flatten(get_all(test_bucket_idx, buckets)))
            yield KFoldIndices(train_idx, valid_idx, test_idx)
