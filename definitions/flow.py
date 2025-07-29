import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from definitions.network_window import NetworkWindow

class Flow:
    def __init__(self, protocol, saddr, sport, daddr, dport):
        self.protocol = protocol
        self.saddr = saddr
        self.sport = sport
        self.daddr = daddr
        self.dport = dport
        self.packets = {}
        self.packets["forward"] = []
        self.packets["backward"] = []
        self.last_timestamp = 0

    def contains(self, pkt):
        protocol, saddr, sport, daddr, dport = pkt.get_each_flow_info()
        forward =  self.protocol == protocol and self.saddr == saddr and self.sport == sport and self.daddr == daddr and self.dport == dport
        backward =  self.protocol == protocol and self.saddr == daddr and self.sport == dport and self.daddr == saddr and self.dport == sport
        return forward or backward

    def is_corresponding_flow(self, flow):
        return self.protocol == flow.get_protocol() and self.saddr == flow.get_saddr() and self.sport == flow.get_sport() and self.daddr == flow.get_daddr() and self.dport == flow.get_dport()

    def get_protocol(self):
        return self.protocol

    def get_saddr(self):
        return self.saddr

    def get_sport(self):
        return self.sport

    def get_daddr(self):
        return self.daddr

    def get_dport(self):
        return self.dport

    def add_packet(self, packet):
        protocol, saddr, sport, daddr, dport = packet.get_each_flow_info()
        forward =  self.protocol == protocol and self.saddr == saddr and self.sport == sport and self.daddr == daddr and self.dport == dport
        backward =  self.protocol == protocol and self.saddr == daddr and self.sport == dport and self.daddr == saddr and self.dport == sport
       
        if packet.get_timestamp() > self.last_timestamp:
            self.last_timestamp = packet.get_timestamp()

        if forward:
            self.packets["forward"].append(packet)
        else:
            self.packets["backward"].append(packet)

    def get_packets(self, direction):
        return self.packets[direction]

    def get_window(self, window_start, window_length):
        if len(self.packets["forward"]) == 0 and len(self.packets["backward"]) == 0:
            return None

        if self.last_timestamp < window_start:
            return None

        window = NetworkWindow(self.protocol, self.saddr, self.sport, self.daddr, self.dport, window_length)
        window_end = window_start + window_length

        for direction in ["forward", "backward"]:
            pkts = self.packets[direction]
            pkts = sorted(pkts, key=lambda x: x.get_timestamp())

            start_found, end_found = False, False
            start_idx, end_idx = 0, -1
            for i in range(len(pkts)):
                if not start_found and pkts[i].get_timestamp() >= window_start:
                    start_found = True
                    start_idx = i

                if not end_found and pkts[i].get_timestamp() > window_end:
                    end_found = True
                    end_idx = i
                
            window.set_packets(direction, pkts[start_idx:end_idx])
        window.set_times(window_start, window_end)
        return window
