from typing import TypeVar, Callable, Generic

PointT = TypeVar('PointT')
RelevantPointT = TypeVar('RelevantPointT', covariant=True)
FeatureT = TypeVar('FeatureT')


class FeatureExtractor(Generic[PointT, RelevantPointT, FeatureT]):
    def __init__(self, data_extractor: Callable[[PointT], RelevantPointT]):
        self._data_extractor = data_extractor

    def _extract(self, data: RelevantPointT) -> FeatureT:
        raise NotImplementedError

    def extract(self, point: RelevantPointT) -> FeatureT:
        return self._extract(self._data_extractor(point))
