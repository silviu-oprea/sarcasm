import os

from ml import TwitterFromWalidLearningDataProvider
from dataio import List
from basic import log
from ml.feature_extractors.vocabulary_based import Vocabulary


logger = log.create_logger('main')

# Paths
root_path = 'resources/data/real/tweets'
tweet_file_path = os.path.join(root_path, 'from_walid.txt')
vocabulary_file_path = os.path.join(root_path, 'vocabulary.txt')

# Data provider and vocabulary
tweet_provider = TwitterFromWalidLearningDataProvider(
    file_path = tweet_file_path, has_header = True, case_sensitive = False)
vocabulary = Vocabulary(case_sensitive = False)

points, _ = tweet_provider.all_data()

# Add all unigrams to vocabulary
for point in points:
    unigram_list = point.get('text', ) \
        .map(lambda text: text.unigrams())\
        .get_or_else(List.empty())
    vocabulary.add(unigram_list)

# Save vocabulary to file
vocabulary.save(vocabulary_file_path)
