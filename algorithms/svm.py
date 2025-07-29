import sys
import copy
import logging
import numpy as np
#import cuml
#from cuml.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from algorithms.algorithm import Algorithm
#import cupy as cp

class Svm(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, step):
        self.scale, dataset = windows.get_dataset(step, scaler="minmax")
        labels = windows.get_labels(step, dl=False)
        logging.info("# of dataset: {}, # of labels: {}".format(len(dataset), len(labels)))

        self.classifier[step] = SVC(kernel='rbf', C=1.0, gamma='scale', verbose=True, probability=True)

        dataset = cp.asarray(dataset)
        labels = cp.asarray(labels)

        try:
            self.classifier[step].fit(dataset, labels)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except:
            self.classifier[step] = None
            logging.info("  => {} {} classifier is not generated".format(self.get_name(), step))

    def detection(self, window, step):
        test = window.get_code()
        test = self.scale.transform(test.reshape(1, -1))
        label = window.get_label(step)
        if self.classifier[step]:
            pred = self.classifier[step].predict_proba(test)
            pred = cp.asnumpy(pred)
            ret = self.classifier[step].predict(test)
            ret = cp.asnumpy(ret)
            logging.debug("label: {}, pred: {}".format(label, pred))
            return ret, list(pred[0])
        else:
            return [0], [0, 1]
