import os, sys, argparse, logging
import time
import threading
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.futils import init_packet_features

class PacketFeatureExtractor:
    def __init__(self, conf):
        self.conf = conf
        self.features = []
        init_packet_features(self)

    def add_feature(self, feature):
        if self.conf[feature.get_name()]:
            self.features.append(feature)
            logging.debug("Feature {} is loaded".format(feature.get_name()))

    def run(self, packets):
        logging.info("Run Packet Feature Extractor")
        self.packets = packets

        for packet in packets:
            self.extract_feature(packet)

    def output(self, odir, ofprefix, interface, timestamp):
        ofname = "{}/{}-{}-{}-packet.csv".format(odir, ofprefix, interface, timestamp)
        packets = self.packets
        features = self.features

        with open(ofname, "w") as of:
            flst = ["source_ip_address", "source_port_number", "destination_ip_address", "destination_port_number"]
            for feature in features:
                flst.append(feature.get_name())
            of.write(','.join(flst))
            of.write(",attack_flag,attack_step,attack_name\n")
            for packet in packets:
                vlst = [packet.get_source_ip_address(), str(packet.get_source_port_number()), packet.get_destination_ip_address(), str(packet.get_destination_port_number())]
                for feature in features:
                    vlst.append(str(packet.get_feature_value(feature.get_name())))
                vlst.append(str(packet.get_attack_flag()))
                vlst.append(packet.get_attack_step())
                vlst.append(packet.get_attack_name())
                of.write(','.join(vlst))
                of.write("\n")

        logging.debug("The packet features are extracted and written in {}".format(ofname))
        return ofname

    def extract_feature(self, packet):
        for f in self.features:
            f.extract_feature(packet)

    def get_packets(self):
        return self.packets

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, help="Configuration file", type=str)
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, "../..")
    c = conf.get("feature_extractor", None)
    if c :
        c = c.get("features", None)
        if c :
            c = c.get("packet", None)
    pfe = PacketFeatureExtractor(c)

    packets = None
    pfe.run(packets)

if __name__ == "__main__":
    main()
