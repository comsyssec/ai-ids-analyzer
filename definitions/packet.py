import socket
import dpkt
import logging

class Packet:
    def __init__(self, ts, eth, network, transport, length):
        self.timestamp = ts
        self.eth = eth
        self.network = network
        self.transport = transport
        self.serial = None
        if self.transport:
            sport = self.transport.sport
            dport = self.transport.dport
            self.label = int(sport / 10000)
            if self.label > 3:
                self.label = 0
        else:
            self.label = 0
        self.length = length
        self.code = {}

        self.stat = {}
        self.attack_flag = 0
        self.attack_step = None
        self.attack_name = None

        self.attack_flag_labeled = 0
        self.attack_step_labeled = None
        self.attack_name_labeled = None

        self.label = None
        self.labeled = None

    def set_serial_number(self, num):
        self.serial = num

    def get_serial_number(self):
        return self.serial

    def set_code(self, name, code):
        self.code[name] = code

    def get_code(self, name):
        return self.code[name]

    def get_timestamp(self):
        return self.timestamp

    def get_ethernet(self):
        return self.eth

    def get_network_layer(self):
        return self.network

    def get_transport_layer(self):
        return self.transport

    def get_header_length(self):
        ret = 0
        ret += 14 # ethernet header length

        if isinstance(self.network, dpkt.ip.IP):
            ip = self.network
            ret += ip.hl

            if ip.p == socket.IPPROTO_TCP:
                tcp = self.transport
                ret += tcp.off
            elif ip.p == socket.IPPROTO_UDP:
                ret += 8
        
        return ret

    def is_fin(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_FIN:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_syn(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if (tcp.flags & dpkt.tcp.TH_SYN) and not (tcp.flags & dpkt.tcp.TH_ACK):
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_rst(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_RST:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_psh(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_PUSH:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_ack(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_ACK:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_urg(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_URG:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_cwr(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_CWR:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_ece(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_ECE:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def get_protocol(self):
        ret = -1
        if isinstance(self.network, dpkt.ip.IP):
            ret = self.network.p
        return ret

    def get_source_ip_address(self):
        ret = "-"
        if isinstance(self.network, dpkt.ip.IP):
            ret = socket.inet_ntop(socket.AF_INET, self.network.src)
        return ret

    def get_destination_ip_address(self):
        ret = "-"
        if isinstance(self.network, dpkt.ip.IP):
            ret = socket.inet_ntop(socket.AF_INET, self.network.dst)
        return ret

    def get_source_port_number(self):
        ret = -1
        if isinstance(self.transport, dpkt.tcp.TCP) or isinstance(self.transport, dpkt.udp.UDP):
            ret = self.transport.sport
        return ret

    def get_destination_port_number(self):
        ret = -1
        if isinstance(self.transport, dpkt.tcp.TCP) or isinstance(self.transport, dpkt.udp.UDP):
            ret = self.transport.dport
        return ret

    def get_flow_info(self):
        saddr = socket.inet_ntop(socket.AF_INET, self.network.src)
        daddr = socket.inet_ntop(socket.AF_INET, self.network.dst)
        if self.transport:
            sport = self.transport.sport % 10000
            dport = self.transport.dport % 10000
            ret = "{}:{}-{}:{}".format(saddr, sport, daddr, dport)
        else:
            ret = "{}-{}".format(saddr, daddr)
        return ret

    def get_each_flow_info(self):
        protocol = self.network.p
        saddr = socket.inet_ntop(socket.AF_INET, self.network.src)
        daddr = socket.inet_ntop(socket.AF_INET, self.network.dst)
        if self.transport:
            sport = self.transport.sport % 10000
            dport = self.transport.dport % 10000
        else:
            sport = None
            dport = None

        return protocol, saddr, sport, daddr, dport

    def set_attack_flag(self, value):
        self.attack_flag = value

    def get_attack_flag(self):
        return self.attack_flag

    def set_attack_flag_labeled(self, value):
        self.attack_flag_labeled = value

    def get_attack_flag_labeled(self):
        return self.attack_flag_labeled

    def set_attack_step(self, value):
        self.attack_step = value
        logging.debug("Packet is set to {}".format(self.attack_step))

    def get_attack_step(self):
        return self.attack_step

    def set_attack_step_labeled(self, value):
        self.attack_step_labeled = value

    def get_attack_step_labeled(self):
        return self.attack_step_labeled

    def set_attack_name(self, value):
        self.attack_name = value

    def get_attack_name(self):
        return self.attack_name

    def set_attack_name_labeled(self, value):
        self.attack_name_labeled = value

    def get_attack_name_labeled(self):
        return self.attack_name_labeled

    def get_packet_length(self):
        return self.length
        #return self.header.getcaplen()

    def add_feature_value(self, feature, val):
        self.stat[feature] = val

    def get_feature_value(self, feature):
        return self.stat.get(feature, None)

    def get_feature_names(self):
        return list(self.stat)
