import sys
import copy
import logging
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
from sklearn.preprocessing import StandardScaler
from six import StringIO
from IPython.display import Image
from algorithms.algorithm import Algorithm

class DecisionTree(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, step):
        #dataset = copy.deepcopy(windows.get_dataset(step))
        self.scale, dataset = windows.get_dataset(step, scaler="standard")
        labels = windows.get_labels(step, dl=False)

        self.classifier[step] = DecisionTreeClassifier()

        try:
            self.classifier[step] = self.classifier[step].fit(dataset, labels)
            logging.info("  => {} {} classifier is generated".format(self.get_name(), step))
        except:
            self.classifier[step] = None
            logging.info("  => {} {} classifier is not generated".format(self.get_name(), step))

    def detection(self, window, step):
        test = window.get_code()
        test = np.array(test)
        test = self.scale.transform(test.reshape(1, -1))
        if self.classifier[step]:
            pred = self.classifier[step].predict_proba(test)
            ret = self.classifier[step].predict(test)
            logging.debug("{}> pred: {}, ret: {}".format(self.get_name(), pred, ret))
            return ret, list(pred[0])
        else:
            logging.debug("{}> pred: {}, ret: {}".format(self.get_name(), pred, ret))
            return [0], [0, 1]
