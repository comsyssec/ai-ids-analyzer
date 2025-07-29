import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from metrics.metric import Metric

class FalsePositive(Metric):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def get_init_value(self):
        # TODO: Implement the following statement to display the result
        return 0

    def get_unit(self):
        return ""

    def evaluate(self, windows, step, amodel):
        # TODO: Implement the procedure to evaluate the model
        aname = amodel.get_name()
        val = 0
        for window in windows:
            if window.get_label(step) == 0:
                if window.get_attack_flag_labeled(step, aname) == 1:
                    val += 1
        if step not in self.values:
            self.values[step] = {}
        self.values[step][aname] = val
        return val


