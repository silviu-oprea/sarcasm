import numpy as np
from typing import Callable, Sequence, TypeVar, Dict, Tuple

from basic.dcollections import setlist
from basic.ditertools import flatten
from ml.feature_extractors.feature_extractor import FeatureExtractor
from tokenization import tokens

TweetT = TypeVar('TweetT')


class HSTFrequencyFeatureExtractor(
        FeatureExtractor[TweetT, Tuple[int, Sequence[tokens.Token]], np.ndarray]):
    def __init__(self,
                 data_extractor: Callable[[TweetT],
                                          Tuple[int, Sequence[tokens.Token]]],
                 hst: Dict[int, Sequence[str]],
                 should_normalize: bool = False):
        self._hst = hst
        self._should_normalize = should_normalize
        super().__init__(data_extractor)

    def _extract(self, data: Tuple[int, Sequence[tokens.Token]]) -> np.ndarray:
        uid, tokens = data
        user_hst = self._hst[uid]
        hist = np.zeros(100)
        for token in tokens:
            try:
                token_hst_index = user_hst.index(str(token.lower()))
                hist[token_hst_index] += 1
            except TypeError:
                pass
        if self._should_normalize:
            hist_sum = sum(hist)
            if hist_sum > 0:
                hist = hist / sum(hist)
        return hist


class HSTGlobalFrequencyFeatureExtractor(
        FeatureExtractor[TweetT, Tuple[int, Sequence[tokens.Token]], np.ndarray]):
    def __init__(self,
                 data_extractor: Callable[[TweetT],
                                          Tuple[int, Sequence[tokens.Token]]],
                 hst: Dict[int, Sequence[str]],
                 should_normalize: bool = False):
        self._hst = setlist(flatten(hst.values()))
        self._should_normalize = should_normalize
        super().__init__(data_extractor)

    def _extract(self, data: Tuple[int, Sequence[tokens.Token]]) -> np.ndarray:
        uid, tokens = data
        hist = np.zeros(len(self._hst))
        for token in tokens:
            try:
                token_hst_index = self._hst.index(str(token.lower()))
                hist[token_hst_index] += 1
            except TypeError:
                pass
        if self._should_normalize:
            hist_sum = sum(hist)
            if hist_sum > 0:
                hist = hist / sum(hist)
        return hist


class HSTIndicatorFeatureExtractor(
        FeatureExtractor[TweetT, Tuple[int, Sequence[tokens.Token]], np.ndarray]):
    def __init__(self,
                 data_extractor: Callable[[TweetT],
                                          Tuple[int, Sequence[tokens.Token]]],
                 hst: Dict[int, Sequence[str]]):
        self._hst = hst
        super().__init__(data_extractor)

    def _extract(self, data: Tuple[int, Sequence[tokens.Token]]) -> np.ndarray:
        uid, tokens = data
        user_hst = self._hst[uid]
        hist = np.zeros(100)
        for token in tokens:
            try:
                token_hst_index = user_hst.index(str(token.lower()))
                hist[token_hst_index] = 1
            except TypeError:
                pass
        return hist


class HSTGlobalIndicatorFeatureExtractor(
        FeatureExtractor[TweetT, Tuple[int, Sequence[tokens.Token]], np.ndarray]):
    def __init__(self,
                 data_extractor: Callable[[TweetT],
                                          Tuple[int, Sequence[tokens.Token]]],
                 hst: Dict[int, Sequence[str]],
                 should_normalize: bool = False):
        self._hst = setlist(flatten(hst.values()))
        self._should_normalize = should_normalize
        super().__init__(data_extractor)

    def _extract(self, data: Tuple[int, Sequence[tokens.Token]]) -> np.ndarray:
        uid, tokens = data
        hist = np.zeros(len(self._hst))
        for token in tokens:
            try:
                token_hst_index = self._hst.index(str(token.lower()))
                hist[token_hst_index] = 1
            except TypeError:
                pass
        return hist
