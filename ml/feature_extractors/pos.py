from itertools import count
from typing import Callable, TypeVar, Sequence

import numpy as np

from ml.feature_extractors.feature_extractor import FeatureExtractor
from tokenization import tokens

TweetT = TypeVar('TweetT')


def token_is_dense(token):
    return (isinstance(token, tokens.NounToken)
            or isinstance(token, tokens.VerbToken)
            or isinstance(token, tokens.AdjectiveToken)
            or isinstance(token, tokens.AdverbToken))


class PosFeatureExtractor(
        FeatureExtractor[TweetT, Sequence[tokens.Token], np.ndarray]):
    """
    1. Count of each of the 25 POS tags
    2. Ratio -"-
    3. Lexical density of the tweet
       That is, the ratio of nouns, verbs, adjectives and adverbs, to all words
    """
    def __init__(self,
                 data_extractor: Callable[[TweetT], Sequence[tokens.Token]]):
        self._token_type_to_index = dict(zip(tokens.all_token_types, count()))
        super().__init__(data_extractor)

    def _extract(self, tokens: Sequence[tokens.Token]):
        pos_count = np.zeros(len(self._token_type_to_index))
        nr_dense_words = 0
        for token in tokens:
            type_index = self._token_type_to_index[type(token)]
            pos_count[type_index] += 1
            if token_is_dense(token):
                nr_dense_words += 1
        pos_ratio = pos_count / len(tokens)
        lexical_density = nr_dense_words / len(tokens)
        return np.concatenate((pos_count, pos_ratio, [lexical_density]))
