import re
from py4j.java_gateway import JavaGateway, GatewayParameters
from nltk.corpus import cmudict

from tokenization.tokens import *


en_dict = cmudict.dict()

positive_emojis = [
    ':-]', ':]', ':-3', ':3', ':->', ':>',  # smileys
    '8-)', '8)', ':-}', ':}', ':o)', ':c)',  # smileys
    ':-))))', ':-)))', ':))))', ':)))', ':))', ':-))',
    ':‑)', ':)', ':^)', '=]', '=)',  # smileys
    '☺', '🙂', '😊', '😀', '😁',  # smileys
    ":'‑)", ":')", '😂',  # tears of laughter
    ':*', ':-*', ':x', '😗', '😙', '😚', '😘', '😍',  # kissing
    # angel, saint, innocent
    'O:‑)', 'O:)', '0:‑3', '0:3', '0:‑)', '0:)', '0;^)', '😇', '👼',
    '#‑)'  # partied all night
]

negative_emojis = [
    ':‑(', ':(', ':‑c', ':c', ':‑<', ':<',  # frown, sad, angry, pouting
    ':‑[', ':[', ':-||', '>:[', ':{', ':@', '>:(',
    '☹', '🙁', '😠', '😡', '😞', '😟', '😣', '😖',
    ":'‑(", ":'(", '😢', '😭',  # crying
    # horror, disgust, saddness, great dismay
    "D‑':", "D:<", "D:", "D8", "D;", "D=", "DX",
    '😨', '😧', '😦', '😱', '😫', '😩',
    # skeptical, annoyed, undecided, uneasy, hesitant
    ':‑/', ':/', ':‑.', '>:\\', '>:/',
    ':\\', '=/', '=\\', ':L', '=L', ':S',
    '🤔', '😕', '😟',
    '>:‑)', '>:)', '}:‑)', '}:)', '3:‑)', '3:)', '>;)',  # evil
    '😈',
    ':‑###..', ':###..',  # being sick
    '🤒', '😷',
    "',:-|", "',:-l",  # scepticism, disbelief, or disapproval
    '<:‑|',  # dumb, dunce-like
    '%‑)', '%)',  # drunk, confused
    '😵', '😕', '🤕'
]

escaped_positive_emojis = [re.escape(w) for w in positive_emojis]
escaped_negative_emojis = [re.escape(w) for w in negative_emojis]

url_regex_v = ('http[s]?:\/\/'
               '(?:[a-zA-Z]'
                  '|[0-9]'
                  '|[$-_@.&+]'
                  '|[!*\(\),]'
                  '|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
url_regex = 'http[s]?:[^ ]+'
word_regex = "[a-zA-Z0-9_']+" + '-?' + "[a-zA-Z0-9_']*"
hashtag_regex = '#' + word_regex
at_regex = "@" + word_regex
punctuation_regex = '\.{3}|\?+|\!+'
positive_emojis_regex = '|'.join(escaped_positive_emojis)
negative_emojis_regex = '|'.join(escaped_negative_emojis)
regex_string = '{}|{}|{}|{}|{}|{}|{}'.format(
    url_regex, at_regex, punctuation_regex,
    word_regex, hashtag_regex,
    positive_emojis_regex, negative_emojis_regex)

generic_stopwords = ['', 'null']
regex_stopwords = ['https?://t.co', '…', '^https?:/?/?(.*\.|)$']
regex_stopwords = [re.compile(r, re.IGNORECASE) for r in regex_stopwords]


def clean(string, case_sensitive=True):
    result = string.strip()
    if not case_sensitive:
        result = result.lower()
    return result


def split(string,
          separator=None,
          case_sensitive=True,
          empty_entries_allowed=True):
    r = [clean(t, case_sensitive) for t in string.split(separator)]
    if not empty_entries_allowed:
        r = [t for t in r if len(t) > 0]
    return r


class StringTokenizer:
    def tokenize(self, s: str) -> list:
        raise NotImplementedError


class CasualStringTokenizer(StringTokenizer):
    class __CasualStringTokenizer(StringTokenizer):
        def __init__(self):
            self._url_regex = re.compile(url_regex, re.IGNORECASE)
            self._at_regex = re.compile(at_regex, re.IGNORECASE)
            self._hashtag_regex = re.compile(hashtag_regex, re.IGNORECASE)
            self._punctuation_regex = re.compile(punctuation_regex, re.IGNORECASE)
            self._word_regex = re.compile(word_regex, re.IGNORECASE)
            self._positive_emojis_regex = re.compile(positive_emojis_regex, re.IGNORECASE)
            self._negative_emojis_regex = re.compile(negative_emojis_regex, re.IGNORECASE)

        def _str_to_token(self, s):
            url_match = self._url_regex.search(s)
            if url_match is not None:
                return UrlToken(url_match.group())

            at_match = self._at_regex.search(s)
            if at_match is not None:
                return AtToken(at_match.group())

            hashtag_match = self._hashtag_regex.search(s)
            if hashtag_match is not None:
                return HashtagToken(hashtag_match.group())

            punctuation_match = self._punctuation_regex.search(s)
            if punctuation_match is not None:
                return PunctuationToken(punctuation_match.group())

            positive_emojis_match = self._positive_emojis_regex.search(s)
            if positive_emojis_match is not None:
                return PositiveEmojiToken(positive_emojis_match.group())

            negative_emojis_match = self._negative_emojis_regex.search(s)
            if negative_emojis_match is not None:
                return NegativeEmojiToken(negative_emojis_match.group())

            word_match = self._word_regex.search(s)
            if word_match is not None:
                return WordToken(word_match.group())

            return None

        def tokenize(self, s):
            str_tokens = split(s)
            tokens = [self._str_to_token(s) for s in str_tokens]
            valid_tokens = [s for s in tokens if s is not None]
            return valid_tokens

    instance = None

    def __init__(self):
        if not CasualStringTokenizer.instance:
                CasualStringTokenizer.instance =\
                    CasualStringTokenizer.__CasualStringTokenizer()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def tokenize(self, s):
        return CasualStringTokenizer.instance.tokenize(s)


class SpaceStringTokenizer(StringTokenizer):
    instance = None

    def __init__(self):
        if not SpaceStringTokenizer.instance:
            SpaceStringTokenizer.instance =\
                SpaceStringTokenizer.__SpaceStringTokenizer()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def tokenize(self, s):
        return self.instance.tokenize(s)

    class __SpaceStringTokenizer(StringTokenizer):
        def __init__(self):
            pass

        def tokenize(self, s):
            return split(s, empty_entries_allowed=False)


class CmuStringTokenizer(StringTokenizer):
    instance = None

    def __init__(self, port):
        if not CmuStringTokenizer.instance:
            CmuStringTokenizer.instance =\
                CmuStringTokenizer.__CmuStringTokenizer(port)
        else:
            CmuStringTokenizer.instance._tagger =\
                CmuStringTokenizer.instance.get_java_tagger(port)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def tokenize(self, s):
        return CmuStringTokenizer.instance.tokenize(s)

    class __CmuStringTokenizer(StringTokenizer):
        def __init__(self, port):
            self._tagger = self.get_java_tagger(port)
            self._cmu_tagset = {
                'N': CommonNounToken,
                'O': PersonalPronounToken,
                '^': ProperNounToken,
                'S': NominalAndPossessiveToken,
                'Z': ProperNounAndPossessiveToken,
                'V': VerbToken,
                'L': NominalAndVerbalToken,
                'M': ProperNounAndVerbalToken,
                'A': AdjectiveToken,
                'R': AdverbToken,
                '!': InterjectionToken,
                'D': DeterminerToken,
                'P': PreOrPostPositionOrSubordinatingConjunctionToken,
                '&': CoordinatingConjunctionToken,
                'T': VerbParticleToken,
                'X': ExistentialOrPredeterminersToken,
                'Y': ExistentialOrPredeterminersAndVerbalToken,
                '#': HashtagToken,
                '@': AtToken,
                '~': DiscourseMarkerToken,
                'U': UrlOrEmailToken,
                'E': self._identify_emoji,
                '$': NumeralToken,
                ',': PunctuationToken,
                'G': OtherToken
            }

        def _identify_emoji(self, s):
            if s in negative_emojis:
                return NegativeEmojiToken(s)
            elif s in positive_emojis:
                return PositiveEmojiToken(s)
            else:
                return EmojiToken(s)

        def get_java_tagger(self, port):
            gateway_param = GatewayParameters(port=port)
            gateway = JavaGateway(gateway_parameters=gateway_param)
            tagger = gateway.entry_point
            return tagger

        def _cmu_token_to_token(self, cmu_token):
            tag = cmu_token.tag()
            s = cmu_token.token()
            return self._cmu_tagset[tag](s)

        def tokenize(self, s):
            cmu_tokens = self._tagger.tokenizeAndTag(s)
            tokens = [self._cmu_token_to_token(ct) for ct in cmu_tokens]
            return tokens


def nltk_count_syllables(word):
    try:
        hyphenation = en_dict[word.lower()]
        counts = [len(list(y for y in x if y[-1].isdigit()))
                  for x in hyphenation]
        return max(counts)
    except KeyError:
        return 0
