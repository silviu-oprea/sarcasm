import logging
from operator import itemgetter

from basic import numpy, functions
from basic.dicttools import merge_dicts
from basic.ditertools import reduce_left

logger = logging.getLogger('ml.models.model_utils')


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
