import os

from basic import log
from ml.feature_extractors.vocabulary_based import Vocabulary

logger = log.create_logger('main')

# Paths
root_path = '/Users/silviu/code/sarcasm/resources/data/real/tweets'
tweet_file_path = os.path.join(root_path, 'from_walid.txt')
vocabulary_file_path = os.path.join(root_path, 'vocabulary.txt')

# Features
vocabulary = Vocabulary.load(vocabulary_file_path, case_sensitive = False)
fes = {
    'text': AttributeFeatureExtractor(
        lambda l: l.get('text', ).map(lambda text: text.unigrams()).get_or_empty()),
    'uid': AttributeFeatureExtractor(lambda l: l.get('fromUserId', ).get(,),
    # 'useless': RandomUselessFeatureExtractor()
    # IdentityFeatureExtractor(),
    'unigram': NGramFrequencyFeatureExtractor(
        vocabulary,
        data_extractor = lambda l: l.get('text', ).map(lambda text: text.unigrams()).get_or_empty()
    )
}

# Data provider and vocabulary
tweet_provider1 = TwitterFromWalidLearningDataProvider(
    file_path = tweet_file_path, has_header = True, case_sensitive = False,
    feature_extractors_dict= fes
)

tweet_provider2 = TwitterFromWalidLearningDataProvider(
    file_path = tweet_file_path, has_header = True, case_sensitive = False,
    feature_extractors_dict= fes
)

merged_provider = MergedLearningDataProvider([tweet_provider1, tweet_provider2])

ten_folds = merged_provider.groupped_k_fold_data(
    k = 10,
    group_key_extractor_list = [
        lambda l: l.get('fromUserId', ).get_or_else(0),
        lambda l: l.get('fromUserId', ).get_or_else(0)
    ]
)

for fold in ten_folds:
    from itertools import count
    print(fold.train_points[0]['text'])
    print([w for w in zip(count(), fold.train_points[0]['unigram']) if w[1] != 0])
    print()

# points, _ = tweet_provider.all_data()
# for point in points:
#     from itertools import count
#     print(point['text'], [w for w in zip(count(), point['unigram']) if w[1] != 0])

# Processing
# for k_fold in tweet_provider.k_fold_data(4):
#     print(k_fold.valid_points)
    # unigram_list = example.point.get('text')\
    #     .map(lambda text: text.unigrams())\
    #     .get_or_else(List.empty())
    # vector = feature_ngram_frequency.compute(unigram_list)
    # print(vector, example.label)
