from itertools import takewhile
from nltk.util import ngrams as nltk_util_ngrams
from typing import Iterable, TypeVar, Iterator, Sequence

import basic
from tokenization import tokens, tokenizers

T = TypeVar('T', covariant=True)


class Line(basic.types.Printable):
    def __init__(self, file_path, line_number, contents):
        self.file_path = file_path
        self.line_number = line_number
        self.contents = contents


# ============================================================================ #
# === Types that represent tokenized strings ================================= #
# ============================================================================ #

class TokenizerError(TypeError):
    def __init__(self, msg):
        self.msg = msg


class NGrams(Sequence[T]):
    def __init__(self, unigrams=None):
        if unigrams is None:
            unigrams = []
        self._ngrams = {1: unigrams}
        self._unigrams = unigrams

    def __iter__(self) -> Iterator[T]:
        return iter(self._ngrams[1])

    def __getitem__(self, idx: int) -> T:
        return self._unigrams[idx]

    def __len__(self) -> int:
        return len(self._unigrams)

    def __str__(self):
        return str(self._unigrams)

    def __repr__(self):
        return repr(self._unigrams)

    def has_valid_tail(self, allowed_tail, case_sensitive=True):
        tail = takewhile(lambda tok: isinstance(tok, tokens.UrlToken) or
                                     isinstance(tok, tokens.HashtagToken),
                         reversed(self._unigrams))
        lower_if_cs = lambda tok: tok if case_sensitive else tok.lower()
        tail = map(lower_if_cs, tail)
        allowed_tail = map(lower_if_cs, allowed_tail)
        return any(tok in tail for tok in allowed_tail)

    def ngrams(self, n):
        stored_ngrams = self._ngrams.get(n)
        if stored_ngrams is None:
            stored_ngrams = nltk_util_ngrams(self, n)
            self._ngrams[n] = list(stored_ngrams)
        return stored_ngrams

    def contains_ngram(self, ngram):
        n = len(ngram)
        return ngram in self.ngrams(n)

    @staticmethod
    def from_string(s, tokenizer, case_sensitive, stopwords, regex_stopwords):
        if not case_sensitive:
            s = s.lower()
            stopwords = map(lambda sw: sw.lower(), stopwords)
        tokens = filter(lambda tok: tok not in stopwords and
                                    all(regex.search(tok) is None
                                        for regex in regex_stopwords),
                        tokenizer.tokenize(s))
        tokens = list(tokens)
        if len(tokens) == 0:
            raise TokenizerError('cannot build NGrams from ' + s)
        return NGrams(tokens)

    @staticmethod
    def get_builder(tokenizer=None, case_sensitive=True,
                    stopwords=None, regex_stopwords=None):
        if tokenizer is None:
            tokenizer = tokenizers.CasualStringTokenizer()
        if stopwords is None:
            stopwords = tokenizers.generic_stopwords
        if regex_stopwords is None:
            regex_stopwords = tokenizers.regex_stopwords
        return lambda s: NGrams.from_string(
            s, tokenizer, case_sensitive, stopwords, regex_stopwords)


SvNgrams = NGrams.get_builder()
CmuNgrams = NGrams.get_builder(
    tokenizer=tokenizers.CmuStringTokenizer(port=10000))


class SpaceTokenizedString:
    def __init__(self, s):
        tokenizer = tokenizers.SpaceStringTokenizer()
        self._tokens = tokenizer.tokenize(s)

    def tokens(self):
        return self._tokens

    def __str__(self):
        return str(self._tokens)

    def __repr__(self):
        return 'SpaceTokenizedString(' + ','.join(self._tokens) + ')'
