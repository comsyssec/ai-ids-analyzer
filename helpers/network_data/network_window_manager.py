import os, sys, argparse, logging
import time
import threading
import copy
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from definitions.flow import Flow
from definitions.packet import Packet

class NetworkWindowManager:
    def __init__(self, conf):
        self.window_length = conf.get("window_length", 1000) / 1000
        self.sliding_window = conf.get("sliding_window", True)
        if self.sliding_window:
            self.sliding_window_interval = conf.get("sliding_window_interval", 100) / 1000
        else:
            self.sliding_window_interval = -1

        if self.sliding_window_interval > self.window_length:
            logging.error("The sliding window interval must be shorter than the window length")
            sys.exit(1)
        self.flows = {}
        self.windows = []
        self.first_timestamp = 0
        self.last_timestamp = 0

    def set_last_timestamp(self, ts):
        self.last_timestamp = ts

    def get_windows(self):
        return self.windows
    
    def run(self, packets):
        self.flows = {}
        self.windows = []
        if self.sliding_window:
            logging.info("Run Network Window Manager with Sliding Window")
        else:
            logging.info("Run Network Window Manager without Sliding Window")

        self.packets = packets
        self.first_timestamp = packets[0].get_timestamp()
        self.last_timestamp = packets[-1].get_timestamp()

        idx = 0

        for packet in packets:
            idx += 1
            self.process_packet(packet)
        
            if idx % 1000 == 0:
                logging.debug("# of packets processed: {}".format(idx))


        logging.debug("sliding_window_interval: {}".format(self.sliding_window_interval))
        logging.debug("window_length: {}".format(self.window_length))
        window_start = self.first_timestamp
        while window_start < self.last_timestamp:
            logging.debug("window_start: {}, self.last_timestamp: {}".format(window_start, self.last_timestamp))
            self.process_window(window_start)
            if self.sliding_window:
                window_start += self.sliding_window_interval
            else:
                window_start += self.window_length

        logging.debug("# of windows: {}".format(len(self.windows)))
   
    def process_packet(self, pkt):
        protocol, saddr, sport, daddr, dport = pkt.get_each_flow_info()
        flow_key = (protocol, saddr, sport, daddr, dport)
        if flow_key in self.flows:
            self.flows[flow_key].add_packet(pkt)
        else:
            flow = Flow(protocol, saddr, sport, daddr, dport)
            flow.add_packet(pkt)
            self.flows[flow_key] = flow

    def process_window(self, window_start):
        for flow in self.flows.values():
            window = flow.get_window(window_start, self.window_length)
            if window:
                self.windows.append(window)
