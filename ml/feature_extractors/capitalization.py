from itertools import count
import numpy as np
from typing import Callable, Any, TypeVar, Sequence

from ml.feature_extractors.feature_extractor import FeatureExtractor
from tokenization import tokens

TweetT = TypeVar('TweetT')


def has_initial_cap(w):
    return len(w) > 0 and w[0].isupper()


def has_all_caps(w):
    return len(w) > 0 and w.isupper()


class CapitalizationFeatureExtractor(
        FeatureExtractor[TweetT, Sequence[tokens.Token], np.ndarray]):
    """
    1. Number of words with initial caps
    2. -"- all caps
    3. Number of POS tags with at least initial caps.
       Interpretation: a vector with an entry for each POS,
       storing the number of that POS occurrences with at least initial caps.
    """

    def __init__(self,
                 data_extractor: Callable[[TweetT], Sequence[tokens.Token]]):
        self._token_type_to_index = dict(zip(tokens.all_token_types, count()))
        super().__init__(data_extractor)

    def _extract(self, tokens: Sequence[tokens.Token]):
        nr_words_initial_caps = 0
        nr_words_all_caps = 0
        nr_capital_pos = np.zeros(len(self._token_type_to_index))
        for token in tokens:
            if has_initial_cap(token):
                nr_words_initial_caps += 1
                type_index = self._token_type_to_index[type(token)]
                nr_capital_pos[type_index] += 1
            if has_all_caps(token):
                nr_words_all_caps += 1
        return np.concatenate((nr_capital_pos,
                               [nr_words_initial_caps, nr_words_all_caps]))
