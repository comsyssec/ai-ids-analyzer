import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from features.feature import Feature

class IsRst(Feature):
    def __init__(self, name):
        super().__init__(name, "packet")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, packet):
        # TODO: Implement the procedure to extract the feature

        if packet.is_rst():
            val = 1
        else:
            val = 0

        packet.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
