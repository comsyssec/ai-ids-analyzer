import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from metrics.metric import Metric

class NumOfTestSamples(Metric):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def get_init_value(self):
        # TODO: Implement the following statement to display the result
        return 0


    def get_unit(self):
        # TODO: Implement the following statement to display the result
        return ""


    def evaluate(self, windows, step, amodel):
        # TODO: Implement the procedure to evaluate the model
        aname = amodel.get_name()
        val = len(windows)

        if step not in self.values:
            self.values[step] = {}
        self.values[step][aname] = val

        return val


