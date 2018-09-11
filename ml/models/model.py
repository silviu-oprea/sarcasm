import logging
import os
from collections import defaultdict

from tensorflow.python import keras as K

module_logger = logging.getLogger('ml.models.model')


class LossHistory(K.callbacks.Callback):
    def on_train_begin(self, logs=None):
        setattr(self, 'losses', defaultdict(list))

    def on_epoch_end(self, epoch, logs=None):
        for k, v in logs.items():
            self.losses[k].append(v)


class Model:
    def __init__(self, nickname):
        self._nickname = nickname
        self._model = self._create_model()

    def __str__(self):
        return self._nickname

    def __repr__(self):
        return self._nickname

    def _process_data(self, points, labels):
        return points, labels

    def _create_model(self):
        raise NotImplementedError

    def train(self, train_points, train_labels,
              valid_points=None, valid_labels=None,
              epochs=10, batch_size=32, verbose=1):
        train_points, train_labels = self._process_data(train_points, train_labels)
        valid_points, valid_labels = self._process_data(valid_points, valid_labels)

        validation_data = None
        if valid_points is not None and valid_labels is not None:
            validation_data = (valid_points, valid_labels)

        metric_collector = LossHistory()
        self._model.fit(train_points, train_labels,
                        callbacks=[metric_collector],
                        validation_data=validation_data,
                        epochs=epochs, batch_size=batch_size,
                        verbose=verbose)
        return metric_collector.losses

    def test_external_metrics(self, test_points, test_labels, metrics, batch_size=32):
        test_points, test_labels = self._process_data(test_points, test_labels)
        pred_labels = self._model.predict(test_points, batch_size)
        results = []
        for metric in metrics:
            module_logger.info('Evaluating ' + metric.__class__.__name__)
            results.append(metric.evaluate(pred_labels, test_labels))
        return results

    def test_internal_metrics(self, test_points, test_labels, batch_size=32, verbose=1):
        metrics = self._model.evaluate(test_points, test_labels, batch_size, verbose=verbose)
        return dict(zip(self._model.metrics_names, metrics))

    def predict(self, points, batch_size=32):
        return self._model.predict(points, batch_size=batch_size)

    def save_weights(self, model_output_dir):
        output_path = os.path.join(model_output_dir, self.name())
        self._model.save(output_path + '.model')
        module_logger.info('Saved model weights to ' + output_path)

    def load_weights(self, model_input_file):
        # Could read from self.name() again but maybe we want more control here.
        # Could also implement both.
        module_logger.info('Loading model weights from ' + model_input_file)
        self._model = K.models.load_model(model_input_file)

    def name(self):
        class_name = self.__class__.__name__
        attrs = ['activation', 'loss', 'optimizer', 'kernel_regularizer', 'input_size']
        attrs_and_names = []
        for attr in attrs:
            if hasattr(self, attr):
                val = getattr(self, attr)
                if not _is_primitive(val):
                    val = val.__class__.__name__
                attrs_and_names.append((attr, val))
        attr_str = '_'.join(attrs_and_names)
        return class_name + '_' + attr_str


def _is_primitive(t):
    primitives = [int, float, str, bool]
    return any(isinstance(t, pt) for pt in primitives)
