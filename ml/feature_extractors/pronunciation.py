import numpy as np
from typing import Callable, TypeVar, Sequence

from basic.ditertools import icount
from ml.feature_extractors.feature_extractor import FeatureExtractor
from tokenization import tokenizers, tokens

TweetT = TypeVar('TweetT')


class PronunciationFeatureExtractor(
        FeatureExtractor[TweetT, Sequence[tokens.Token], np.ndarray]):
    def __init__(self,
                 data_extractor: Callable[[TweetT], Sequence[tokens.Token]]):
        self._lc_vowels = {'a', 'e', 'i', 'o', 'y', 'u'}
        super().__init__(data_extractor)

    def _count_vowels(self, w):
        nr_vowels = len(list(filter(lambda c: c in self._lc_vowels, w.lower())))
        return nr_vowels

    def _extract(self, tokens: Sequence[tokens.Token]):
        nr_tokens_without_vowels = icount(
            lambda token: self._count_vowels(token) == 0, tokens)
        nr_polysyllables = icount(
            lambda token: tokenizers.nltk_count_syllables(str(token)) > 3, tokens)
        return np.array([nr_tokens_without_vowels, nr_polysyllables])
