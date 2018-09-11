from tensorflow.python import keras as K

from ml.models.model import Model


class BinaryLogisticRegression(Model):
    def __init__(self, input_size,
                 loss='binary_crossentropy',
                 activation='sigmoid',
                 optimizer='adam',
                 l2_param=0.01,
                 nickname=None,
                 metrics=None):
        if metrics is None:
            metrics = ['binary_accuracy']
        if nickname is None:
            nickname = ('{}({})'.format(self.__class__.__name__, l2_param))

        self._input_size = input_size
        self._loss = loss
        self._activation = activation
        self._optimizer = optimizer
        self._metrics = metrics
        self._kernel_regularizer = K.regularizers.l2(l2_param)
        super().__init__(nickname)

    def _create_model(self):
        x = K.layers.Input(shape=(self._input_size,))
        y = K.layers.Dense(1, activation='sigmoid', kernel_regularizer=self._kernel_regularizer)(x)
        model = K.Model(inputs=x, outputs=y)
        model.compile(optimizer=self._optimizer, loss=self._loss, metrics=self._metrics)
        return model
