import logging
import numpy as np
from itertools import count
from typing import Callable, Sequence, TypeVar
from nltk.util import ngrams as nltk_util_ngrams

from dataio import iotypes
from ml.feature_extractors.feature_extractor import FeatureExtractor

logger = logging.getLogger('ml.feature_extractors.vocabulary_based')
TweetT = TypeVar('TweetT')


class NGramFrequencyFeatureExtractor(
        FeatureExtractor[TweetT, iotypes.NGrams, np.ndarray]):
    def __init__(self, data_extractor: Callable[[TweetT], iotypes.NGrams],
                 vocabulary: Sequence[str], n: int = 1,
                 should_normalise: bool = False):
        super().__init__(data_extractor)
        if n > 1:
            vocabulary = nltk_util_ngrams(vocabulary, n)
        self._n = n
        self._should_normalise = should_normalise
        self._word_to_vocab_idx = dict(zip(vocabulary, count()))

    def _extract(self, ngrams_obj: iotypes.NGrams) -> np.ndarray:
        ngrams = ngrams_obj.ngrams(self._n)
        histogram = np.zeros(len(self._word_to_vocab_idx))
        for ngram in ngrams:
            idx_in_vocab = self._word_to_vocab_idx.get(ngram.extract().lower())
            if idx_in_vocab is not None:
                histogram[idx_in_vocab] += 1
        if self._should_normalise:
            histogram_sum = sum(histogram)
            if histogram_sum > 0:
                histogram = histogram / sum(histogram)
        return histogram


class NGramIndicatorFeatureExtractor(
        FeatureExtractor[TweetT, iotypes.NGrams, np.ndarray]):
    def __init__(self, data_extractor: Callable[[TweetT], iotypes.NGrams],
                 vocabulary: Sequence[str], n: int = 1,
                 should_normalise: bool = False):
        super().__init__(data_extractor)
        if n > 1:
            vocabulary = nltk_util_ngrams(vocabulary, n)
        self._n = n
        self._should_normalise = should_normalise
        self._word_to_vocab_idx = dict(zip(vocabulary, count()))

    def _extract(self, ngrams_obj: iotypes.NGrams) -> np.ndarray:
        ngrams = ngrams_obj.ngrams(self._n)
        indicator = np.zeros(len(self._word_to_vocab_idx))
        for ngram in ngrams:
            idx_in_vocab = self._word_to_vocab_idx.get(ngram.extract().lower())
            if idx_in_vocab is not None:
                indicator[idx_in_vocab] = 1
        return indicator
