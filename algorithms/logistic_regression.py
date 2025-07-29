import sys
import copy
import logging
import numpy as np
import sklearn.linear_model
from sklearn.preprocessing import StandardScaler
from algorithms.algorithm import Algorithm

class LogisticRegression(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, step):
        self.scale, dataset = windows.get_dataset(step, scaler="standard")
        labels = windows.get_labels(step, dl=False)
        cnt = 0
        for l in labels:
            if l > 0:
                cnt += 1
        self.classifier[step] = sklearn.linear_model.LogisticRegression(verbose=0, max_iter=1000)
        try:
            self.classifier[step] = self.classifier[step].fit(dataset, labels)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except:
            self.classifier[step] = None
            logging.info("  => {} {} classifier is not generated".format(self.get_name(), step))

    def detection(self, window, step):
        test = window.get_code()
        test = self.scale.transform(test.reshape(1, -1))
        label = window.get_label(step)
        if self.classifier[step]:
            ret = self.classifier[step].predict(test)
            pred = self.classifier[step].predict_proba(test)
            logging.debug("{}> pred: {}, ret: {}".format(self.get_name(), pred, ret))
            return ret, list(pred[0])
        else:
            return [0], [0, 1]
