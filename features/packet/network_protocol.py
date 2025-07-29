import os, sys, logging
import pathlib
import dpkt
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from features.feature import Feature

class NetworkProtocol(Feature):
    def __init__(self, name):
        super().__init__(name, "packet")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, packet):
        # TODO: Implement the procedure to extract the feature
        ethernet = packet.get_ethernet()
        if ethernet.type == dpkt.ethernet.ETH_TYPE_IP:
            val = "IP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_EDP:
            val = "EDP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_PUP:
            val = "PUP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_ARP:
            val = "ARP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_AOE:
            val = "AOE"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_CDP:
            val = "CDP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_DTP:
            val = "DTP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_REVARP:
            val = "REVARP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_8021Q:
            val = "802.1Q"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_8021AD:
            val = "802.1AD"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_QINQ1:
            val = "QINQ"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_QINQ2:
            val = "QINQ"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_IPX:
            val = "IPX"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_IP6:
            val = "IPv6"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_PPP:
            val = "PPP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_MPLS:
            val = "MPLS"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_MPLS_MCAST:
            val = "MPLS Multicast"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_PPPoE_DISC:
            val = "PPPoE DISC"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_PPPoE:
            val = "PPPoE"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_LLDP:
            val = "LLDP"
        elif ethernet.type == dpkt.ethernet.ETH_TYPE_TEB:
            val = "TEB"
        else:
            val = "unknown"

        packet.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
