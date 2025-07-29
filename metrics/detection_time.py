import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from metrics.metric import Metric
from sklearn import metrics as m

class DetectionTime(Metric):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def get_init_value(self):
        # TODO: Implement the following statement to display the result
        return 0.0

    def get_unit(self):
        return "s"

    def evaluate(self, windows, step, amodel):
        # TODO: Implement the procedure to evaluate the model
        aname = amodel.get_name()
        detection_times = []

        for window in windows:
            detection_times.append(window.get_detection_time(step, aname))

        val = round(sum(detection_times) / len(detection_times), 2)
        if step not in self.values:
            self.values[step] = {}
        self.values[step][aname] = val
        logging.debug(" {} - {}: {}".format(step, aname, val))
        return val


