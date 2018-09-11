import logging

from basic import log
from dataio import PipingProvider
from dataio.tokenization_types import NGrams

logger = log.create_logger('main')
kfold_logger = log.create_logger('kfold', level=logging.INFO)
data_provider_logger = log.create_logger('data_provider', level=logging.INFO)

# Paths
root_path = '/Users/silviu/code/sarcasm/resources/pipeline/examples'

json_schema = {
    # 'created_at': FilteredString,
    'id': int,
    # 'text': CmuNgrams,
    'text': NGrams.from_json,
    'truncated': bool,
    'in_reply_to_status_id': int,
    'in_reply_to_user_id': int,
    'retweeted_status': {},
    'lang': str,
    'user': {
        'id': int,
        'name': str
    }
}

schema = {'point': json_schema, 'label': int}

# d1 = file_provider.path_to_rec_named_line_it(root_path, min_lines=2)
d2 = PipingProvider.recursive_from_path(root_path, min_lines=2) \
    .tokenize_json(schema)

print(d2.examples['positive.json'].map(lambda l: l.get('point').get('id')).collect())
