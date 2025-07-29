import sys
import copy
import logging
import numpy as np
from algorithms.algorithm import Algorithm
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.metrics import Recall, Precision
from sklearn.preprocessing import MinMaxScaler, StandardScaler

THRESHOLD=0.5
BATCH=256
EPOCHS=50

class Feedforward(Algorithm):
    def __init__(self, name):
        super().__init__(name)
        self.num = {}
        self.num["training"] = {}
        self.num["testing"] = {}

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, step):
        self.scale, dataset = windows.get_dataset(step, scaler="minmax")
        dataset = dataset.reshape((dataset.shape[0], 1, dataset.shape[1]))
        features = len(windows.get_feature_names())
        labels = windows.get_labels(step, dl=True)

        self.classifier[step] = Sequential()
        self.classifier[step].add(Dense(128, activation='relu'))
        self.classifier[step].add(Dense(128, activation='relu'))
        self.classifier[step].add(Dense(1, activation='sigmoid'))
        self.classifier[step].compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        try:
            self.classifier[step].fit(dataset, labels, epochs=EPOCHS, batch_size=BATCH, verbose=1)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except:
            self.classifier[step] = None
            logging.info("  => {} {} classifier is not generated".format(self.get_name(), step))

    def detection(self, window, step):
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
                    #test = window.get_code().copy()
                    test = window.get_code()
                    test = np.array(test)
                    test = self.scale.transform(test.reshape(1, -1))
                    test = test.reshape((test.shape[0], 1, test.shape[1]))
                    tests.append(test)
                    labels.append(label)

                rest = BATCH - len(tests)
                for _ in range(rest):
                    code = [-1] * nfeatures
                    code = np.array(code)
                    code = self.scale.transform(code.reshape(1, -1))
                    code = code.reshape((code.shape[0], 1, code.shape[1]))
                    tests.append(code)
                    labels.append(-1)

                tests = np.concatenate(tests, axis=0)
                labels = np.array(labels)

                preds = self.classifier[step].predict(tests, batch_size=BATCH)

                if rest > 0:
                    preds = preds[:-1*rest]
                    labels = labels[:-1*rest]

                ret = []
                probs = []
                idx = 0
                for pred in preds:
                    val = float(pred[0][0])

                    prob = [1-val, val]
                    probs.append(prob)
                    ret.append(int(val > THRESHOLD))

                    logging.debug("label: {}, pred: {}, ret: {}".format(label, pred, ret))

                    idx += 1
                self.flush(step)
                return ret, probs
            else:
                return None
