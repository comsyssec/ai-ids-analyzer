import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from metrics.metric import Metric

class FeatureImportance(Metric):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def get_init_value(self):
        # TODO: Implement the following statement to display the result
        return None


    def get_unit(self):
        # TODO: Implement the following statement to display the result
        return ""


    def evaluate(self, windows, step, amodel):
        # TODO: Implement the procedure to evaluate the model
        val = ""
        aname = amodel.get_name()
        if hasattr(amodel, "classifier"):
            if step in amodel.classifier:
                if hasattr(amodel.classifier[step], "feature_importances_"):
                    fnames = windows[0].get_feature_names()
                    lst = amodel.classifier[step].feature_importances_
                    top5_idx = []

                    while len(top5_idx) < 5:
                        v = -1
                        i = -1 
                        for idx in range(len(lst)):
                            if idx not in top5_idx:
                                if lst[idx] > v:
                                    v = lst[idx]
                                    i = idx
                        top5_idx.append(i)

                    top5 = []
                    for idx in top5_idx:
                        top5.append(fnames[idx])
                    val = '/'.join(top5)
        if step not in self.values:
            self.values[step] = {}
        self.values[step][aname] = val
        return val


