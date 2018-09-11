import logging
import os
from typing import List, Sequence

import numpy as np

from basic import filesystem
from dataio.fileio import writers as fwrite_utils
from dataio.iopipes import Pipe
from ml.feature_extractors.feature_extractor import FeatureExtractor
from ml.feature_extractors.historical_salient_terms import HSTIndicatorFeatureExtractor
from ml.kfold import GroupedKFold
from ml.models import model_utils
from ml.models.simple import BinaryLogisticRegression
from serialization.ml.kfold import KFoldIndicesSerializer, KFoldIndicesDeserializer
from staging.pipeline.types import Tweet

logger = logging.getLogger('modelling')


def gen_kfold(k, points, labels, split_spec, kfold_dir):
    kfolds_file = os.path.join(kfold_dir, '{}.json'.format(k))

    if not filesystem.readable_file(kfolds_file):
        logger.info('[gen_kfold] Generating {} folds in {}'
                    .format(k, kfolds_file))
        key_extractor = lambda point: point.uid
        kfolds = list(GroupedKFold(k, key_extractor).split(
            points, labels, split_spec))
        fwrite_utils.it_to_file(kfolds, kfolds_file, KFoldIndicesSerializer)
        return kfolds

    logger.info('[get_kfold] Reading {} folds from {}'.format(k, kfolds_file))
    kfolds_it = Pipe.from_path(kfolds_file, KFoldIndicesDeserializer)
    return kfolds_it


def train_model(features, labels, kfolds, epochs=1, batch_size=32, verbose=1):
    input_size = len(features[0])
    models = [BinaryLogisticRegression(input_size, l2_param=0.1),
              BinaryLogisticRegression(input_size, l2_param=0.01)]
    run_cv(models, kfolds, features, labels, epochs, batch_size, verbose)


# in kfold/<fold_idx>:
# stats/hst.json
# stats/topics.json
# features.json
# test mode: don't generate stats, read them
# or just
def get_features(fold_idx: int,
                 points: Sequence[Tweet], labels: Sequence[int],
                 train_idx: Sequence[int], valid_idx: Sequence[int],
                 test_idx: Sequence[int], fe: FeatureExtractor):



def run_cv(models, fe, kfolds, points, labels,
           epochs=10, batch_size=32, verbose=1):
    all_metrics = []
    all_best_models = []
    for idx, (train_idx, valid_idx, test_idx) in enumerate(kfolds, start=1):
        train_points = points[train_idx]
        valid_points = points[valid_idx]
        test_points = points[test_idx]

        train_labels = labels[train_idx]
        valid_labels = labels[valid_idx]
        test_labels = labels[test_idx]

        logger.info('[run_cv] Starting fold {}'
                    '\n\ttrain: {} examples with distribution {}'
                    '\n\tvalid: {} examples with distribution {}'
                    '\n\ttest:  {} examples with distribution {}'
                    .format(idx,
                            len(train_labels), numpy.histogram(train_labels),
                            len(valid_labels), numpy.histogram(valid_labels),
                            len(test_labels), numpy.histogram(test_labels)))
        models_and_losses = []
        for model in models:
            losses = model.train(
                train_points, train_labels,
                valid_points=valid_points, valid_labels=valid_labels,
                epochs=epochs, batch_size=batch_size, verbose=verbose)
            models_and_losses.append((model, min(losses['val_loss'])))

        best_model, _ = min(models_and_losses, key=itemgetter(1))
        fold_metrics = best_model.test_internal_metrics(
            test_points, test_labels)
        logger.info('[run_cv] Finished fold ' + str(idx))
        all_metrics.append(fold_metrics)
        all_best_models.append(best_model)

    metrics_avg = reduce_left(
        lambda m1, m2: merge_dicts(m1, m2,
                                   merger=lambda e1, e2: (e1 + e2) / 2),
        all_metrics)
    for metrics, model in zip(all_metrics, all_best_models):
        logger.info('[run_cv] {} with {}'.format(metrics, model))
    logger.info('[run_cv] Summary: ' + str(metrics_avg))
