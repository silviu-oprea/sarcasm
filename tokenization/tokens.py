class Token(str):
    def __new__(cls, str_):
        return super(Token, cls).__new__(cls, str_)

    def __eq__(self, other):
        return type(self) is type(other) and str.__eq__(self, other)

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self))

    def eq(self, other, case_sensitive=True):
        if case_sensitive:
            return self == other
        else:
            return self.lower() == other.lower()

    def lower(self):
        return self.__class__(str.lower(self))

    def extract(self):
        return str.__str__(self)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self)


class NounToken(Token): pass
class CommonNounToken(NounToken): pass
class ProperNounToken(NounToken): pass
class AdjectiveToken(Token): pass
#
# Should these be more specialized?
class PronounToken(Token): pass
class PersonalPronounToken(PronounToken): pass
#
class VerbToken(Token): pass
class AdverbToken(Token): pass
#
class InterjectionToken(Token): pass
class DeterminerToken(Token): pass
class PreOrPostPositionOrSubordinatingConjunctionToken(Token): pass
class CoordinatingConjunctionToken(Token): pass
class VerbParticleToken(Token): pass
class ExistentialOrPredeterminersToken(Token): pass
class ExistentialOrPredeterminersAndVerbalToken(Token): pass
#
class HashtagToken(Token): pass
class AtToken(Token): pass
class DiscourseMarkerToken(Token): pass
class UrlOrEmailToken(Token): pass
#
class EmojiToken(Token): pass
class PositiveEmojiToken(EmojiToken): pass
class NegativeEmojiToken(EmojiToken): pass
#
class NumeralToken(Token): pass
class PunctuationToken(Token): pass
#
class NominalAndPossessiveToken(Token): pass
class ProperNounAndPossessiveToken(Token): pass
class NominalAndVerbalToken(Token): pass
class ProperNounAndVerbalToken(Token): pass
#
class OtherToken(Token): pass
class WordToken(Token): pass
class UrlToken(Token): pass


all_token_types = [
    NounToken,
    CommonNounToken,
    ProperNounToken,
    AdjectiveToken,
    PronounToken,
    PersonalPronounToken,
    VerbToken,
    AdverbToken,
    InterjectionToken,
    DeterminerToken,
    PreOrPostPositionOrSubordinatingConjunctionToken,
    CoordinatingConjunctionToken,
    VerbParticleToken,
    ExistentialOrPredeterminersToken,
    ExistentialOrPredeterminersAndVerbalToken,
    HashtagToken,
    AtToken,
    DiscourseMarkerToken,
    UrlOrEmailToken,
    EmojiToken,
    PositiveEmojiToken,
    NegativeEmojiToken,
    NumeralToken,
    PunctuationToken,
    NominalAndPossessiveToken,
    ProperNounAndPossessiveToken,
    NominalAndVerbalToken,
    ProperNounAndVerbalToken,
    UrlToken,
    OtherToken,
    WordToken
]
