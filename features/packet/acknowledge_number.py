import os, sys, logging
import dpkt, socket
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from features.feature import Feature

class AcknowledgeNumber(Feature):
    def __init__(self, name):
        super().__init__(name, "packet")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, packet):
        # TODO: Implement the procedure to extract the feature
    
        ip = packet.get_network_layer()
        if ip.p != socket.IPPROTO_TCP:
            val = -1
        else:
            tcp = packet.get_transport_layer()
            if isinstance(tcp, dpkt.tcp.TCP):
                val = tcp.ack
            else:
                val = -1

        packet.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
