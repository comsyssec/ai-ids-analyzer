import os, sys, argparse, logging
import time
import dpkt
import socket
from scapy.all import PcapReader
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from definitions.packet import Packet
from definitions.packet_header import PacketHeader

class PacketReader:
    def __init__(self, conf):
        self.packets = []
        self.config = conf

    def run(self, pname, lname):
        self.packets = []
        ret = ["all"]
        flags, steps, names = parse_label(lname)
        logging.debug("# of labels: {}".format(len(flags)))

        num = 0
        with PcapReader(pname) as pcap:
            for packet in pcap:
                pbytes = bytes(packet)
                pkt = parse_packet(packet.time, pbytes)
                num += 1
            
                if pkt:
                    try:
                        pkt.set_attack_flag(flags[num])
                        pkt.set_attack_step(steps[num])
                        pkt.set_attack_name(names[num])

                        if steps[num] not in ret:
                            if steps[num] not in ["benign", "-"]:
                                ret.append(steps[num])
                    except:
                        logging.error("  => Exception happens in parsing the packets")
                        pkt.set_attack_flag(0)
                        pkt.set_attack_step("benign")
                        pkt.set_attack_name("benign")

                    self.packets.append(pkt)
                if num % 1000 == 0:
                    logging.debug("# of packets parsed: {}".format(num))
        self.packets = sorted(self.packets, key=lambda x: x.get_timestamp())
        return ret

    def get_packets(self):
        return self.packets

def parse_packet(ts, packet):
    try:
        eth = dpkt.ethernet.Ethernet(packet)
    except dpkt.dpkt.NeedData as e:
        logging.error(f"NeedData error:{e}")
        return None

    if not isinstance(eth.data, dpkt.ip.IP):
        logging.error("Non IP packet type not supported: {}".format(eth.data.__class__.__name__))
        return None

    length = len(packet)
    ip = eth.data
    df = bool(ip.off & dpkt.ip.IP_DF)
    mf = bool(ip.off & dpkt.ip.IP_MF)
    offset = bool(ip.off & dpkt.ip.IP_OFFMASK)

    protocol = ip.p
    trans = None

    if protocol == 1:
        logging.debug("ICMP: {} -> {}".format(inet_to_str(ip.src), inet_to_str(ip.dst)))

    elif protocol == 6:
        if not isinstance(ip.data, dpkt.tcp.TCP):
            logging.error("TCP error")
            return None
        tcp = ip.data
        sport = tcp.sport
        dport = tcp.dport
        logging.debug("TCP/IP: {}:{} -> {}:{} (len={})".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport, ip.len))
        trans = tcp
        key = "{}:{}:{}:{}".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport)

    elif protocol == 17:
        if not isinstance(ip.data, dpkt.udp.UDP):
            logging.error("UDP error")
            return None
        udp = ip.data
        sport = udp.sport
        dport = udp.dport
        logging.debug("UDP/IP: {}:{} -> {}:{} (len={})".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport, ip.len))
        trans = udp
        key = "{}:{}:{}:{}".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport)

    else:
        logging.error("Not supported protocol")
        return None

    return Packet(ts, eth, ip, trans, length)

def parse_label(lname):
    flag = {}
    udl = {}
    name = {}
    with open(lname, "r") as f:
        for line in f:
            try:
                tmp = line.strip().split(",")
                idx = int(tmp[0])
                flag[idx] = int(tmp[-1])
                udl[idx] = tmp[-2]
                name[idx] = tmp[-3]
            except:
                continue
    return flag, udl, name

def inet_to_str(addr):
    try:
        return socket.inet_ntop(socket.AF_INET, addr)
    except:
        return socket.inet_ntop(socket.AF_INET6, addr)

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Configuration file", type=str, default="../config.yaml")
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, "..")
    c = conf.get("feature_extractor", None)
    if c != None:
        c = c.get("packet_reader", None)
    packet_reader = PacketReader(c)

if __name__ == "__main__":
    main()
