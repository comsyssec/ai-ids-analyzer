import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from metrics.metric import Metric
from sklearn import metrics as m

class Recall(Metric):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def get_init_value(self):
        # TODO: Implement the following statement to display the result
        return 0.0

    def get_unit(self):
        return "%"

    def evaluate(self, windows, step, amodel):
        # TODO: Implement the procedure to evaluate the model
        aname = amodel.get_name()
        test_labels = []
        predicted_labels = []

        for window in windows:
            test_labels.append(window.get_label(step))
            predicted_labels.append(window.get_attack_flag_labeled(step, aname))

        val = round(m.recall_score(test_labels, predicted_labels, zero_division=0) * 100.0, 2)
        if step not in self.values:
            self.values[step] = {}
        self.values[step][aname] = val
        return val


