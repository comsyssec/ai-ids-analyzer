import os, sys, logging
import dpkt
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from features.feature import Feature

class SourceMacAddress(Feature):
    def __init__(self, name):
        super().__init__(name, "packet")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, packet):
        # TODO: Implement the procedure to extract the feature

        eth = packet.get_ethernet()
        val = -1
        if isinstance(eth, dpkt.ethernet.Ethernet):
            val = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(eth.src[0], eth.src[1], eth.src[2], eth.src[3], eth.src[4], eth.src[5])

        packet.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
