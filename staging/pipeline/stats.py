import heapq
import logging
import typing as t
from collections import namedtuple, defaultdict

import math
from operator import itemgetter

from basic.dcollections import orderedset
from basic.dicttools import map_values
from basic.stattools import histogram
from staging.pipeline.types import Example

logger = logging.getLogger('stats')


class StatBuilder:
    def add(self, ex: Example):
        raise NotImplementedError


class VocabularyStatBuilder(StatBuilder):
    def __init__(self, initial: t.Iterator[str] = None):
        if initial is None:
            initial = []
        # sort_key = lambda x: x.lower() if x[0].isupper() else x.upper()
        self.set = orderedset()
        self.set.update(initial)

    def add(self, ex: Example):
        self.set.update(map(lambda word: word.lower(), ex.point.text))

    def get(self) -> list:
        return list(self.set)


HstStat = namedtuple('HstStat', ['uid', 'hst'], verbose=False)
class HstStatBuilder(StatBuilder):
    def __init__(self, uid: int, nr_terms: int = 100):
        self._uid = uid
        self._nr_terms = nr_terms
        self._term_hists = []
        self._term_to_idf = defaultdict(int)
        self._nr_docs = 0

    def add(self, ex: Example):
        terms = list(map(lambda w: w.lower(), ex.point.text))
        term_hist = map_values(lambda tf: tf / len(terms), histogram(terms))
        for term in term_hist.keys():
            self._term_to_idf[term] += 1
        self._term_hists.append(term_hist)
        self._nr_docs += 1

    def get(self) -> HstStat:
        heap = defaultdict(int)
        for term_hist in self._term_hists:
            for term, tf in term_hist.items():
                raw_idf = max(1, self._term_to_idf[term])
                idf = math.log(self._nr_docs / raw_idf)
                tfidf = tf * idf
                heap[term] = max(tfidf, heap[term])
        term_with_tfidf = heapq.nlargest(
            self._nr_terms, heap.items(), key=itemgetter(1))
        hst = list(map(itemgetter(0), term_with_tfidf))
        return HstStat(self._uid, hst)


TopicsStat = namedtuple('TopicsStat', ['uid', 'topics'], verbose=False)
class TopicsStatBuilder(StatBuilder):
    def __init__(self, uid):
        self.uid = uid
        self.topics = ['topic1', 'topic2']

    def add(self, ex: Example):
        pass

    def get(self) -> TopicsStat:
        return TopicsStat(self.uid, self.topics)


AllStats = namedtuple('AllStats', ['vocab', 'hst', 'topics'], verbose=False)
