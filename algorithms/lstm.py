import sys
import copy
import logging
import numpy as np
from algorithms.algorithm import Algorithm
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Activation
from keras.layers import Dropout
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

TIME_STEP = 2
THRESHOLD = 0.5
BATCH = 256
EPOCHS = 1

class Lstm(Algorithm):
    def __init__(self, name):
        super().__init__(name)
        self.num = {}
        self.num["training"] = {}
        self.num["testing"] = {}

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, step):
        self.scale, dataset = windows.get_dataset(step, scaler="minmax")
        fallback = False
        try:
            dataset = dataset.reshape((dataset.shape[0], TIME_STEP, int(dataset.shape[1] / TIME_STEP)))
        except:
            fallback = True
            dataset = dataset.reshape((dataset.shape[0], 1, dataset.shape[1]))

        labels = windows.get_labels(step, dl=True)
        features = len(windows.get_feature_names())
        
        dataset = dataset[:(len(dataset) // BATCH) * BATCH]
        labels = labels[:(len(labels) // BATCH) * BATCH]

        self.classifier[step] = Sequential()
        if fallback:
            self.classifier[step].add(LSTM(128, return_sequences=True, activation='tanh', recurrent_activation="sigmoid"))
        else:
            self.classifier[step].add(LSTM(128, return_sequences=True, activation='tanh', recurrent_activation="sigmoid"))
        self.classifier[step].add(LSTM(128, return_sequences=True, activation='tanh', recurrent_activation="sigmoid"))
        self.classifier[step].add(Dense(1, activation='sigmoid'))
        self.classifier[step].compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        try:
            self.classifier[step].fit(dataset, labels, epochs=EPOCHS, batch_size=BATCH, validation_split=0.2, verbose=1)
            if fallback:
                logging.info("  => {} {} classifier is generated with the time step 1".format(self.get_name(), step))
            else:
                logging.info("  => {} {} classifier is generated with the time step {}".format(self.get_name(), step, TIME_STEP))
        except:
            self.classifier[step] = None
            logging.info("  => {} {} classifier is not generated".format(self.get_name(), step))

    def detection(self, window, step):
        logging.debug("window.get_code(): {}".format(window.get_code()))
        if step not in self.num["testing"]:
            self.num["testing"][step] = 0
        self.num["testing"][step] += 1
        total = self.get_num_of_windows(False)
        self.enqueue(step, window)
        if self.get_num_item(step) < BATCH and self.num["testing"][step] < total:
            return None
        else:
            windows = self.get_queue(step)
            tests = []
            labels = []
            if len(windows) > 0:
                nfeatures = len(windows[0].get_code())
                for window in windows:
                    label = window.get_label(step)
                    test = window.get_code()
                    test = np.array(test)
                    test = self.scale.transform(test.reshape(1, -1))
                    fallback = False
                    try:
                        test = test.reshape((test.shape[0], TIME_STEP, int(test.shape[1] / TIME_STEP)))
                    except:
                        fallback = True
                        test = test.reshape((test.shape[0], 1, test.shape[1]))
                    tests.append(test)
                    labels.append(label)

                rest = BATCH - len(tests)
                for _ in range(rest):
                    code = [-1] * nfeatures
                    code = np.array(code)
                    code = self.scale.transform(code.reshape(1, -1))
                    try:
                        code = code.reshape((code.shape[0], TIME_STEP, int(code.shape[1] / TIME_STEP)))
                    except:
                        code = code.reshape((code.shape[0], 1, code.shape[1]))
                    tests.append(code)
                    labels.append(-1)

                tests = np.concatenate(tests, axis=0)
                labels = np.array(labels)

                preds = self.classifier[step].predict(tests, batch_size=BATCH)

                if rest > 0:
                    preds = preds[:-1*rest]
                    labels = labels[:-1:rest]

                ret = []
                probs = []
                idx = 0
                for pred in preds:
                    val = float(pred[0][0])

                    prob = [1-val, val]
                    probs.append(prob)
                    ret.append(int(val > THRESHOLD))

                    if fallback:
                        logging.debug("lstm> idx: {}, label: {}, pred: {}, ret: {}, time_step: 1".format(idx, label, pred, ret))
                    else:
                        logging.debug("lstm> idx: {}, label: {}, pred: {}, ret: {}, time_step: {}".format(idx, label, pred, ret, TIME_STEP))
                    idx += 1

                self.flush(step)
                return ret, probs
            else:
                return None
