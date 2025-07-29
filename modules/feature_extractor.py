import os, sys, argparse, logging
import yaml, json, time
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.etc import process_error
from modules.module import Module
from helpers.network_data.packet_reader import PacketReader
from helpers.network_data.network_window_manager import NetworkWindowManager
from helpers.network_data.packet_feature_extractor import PacketFeatureExtractor
from helpers.network_data.flow_feature_extractor import FlowFeatureExtractor

class FeatureExtractor(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize FeatureExtractor")
        super().__init__(core, conf)
        c = conf.get("packet_reader", None)
        self.packet_reader = PacketReader(c)

        c = conf.get("network_window_manager", None)
        self.network_window_manager = NetworkWindowManager(c)

        c = conf.get("features", None)
        if c:
            c = c.get("packet", None)
        self.packet_feature_extractor = PacketFeatureExtractor(c)

        c = conf.get("features", None)
        if c:
            c = c.get("flow", None)
        self.flow_feature_extractor = FlowFeatureExtractor(c)

    def run(self, pname=None, nlname=None, odir=None, phase=None, timestamp=None):
        logging.info("Running the feature extractor")
        steps = []

        if not odir:
            odir = self.get_output_directory()
            if not odir:
                odir = root_directory

        if not phase:
            phase = self.get_output_file_prefix()
            if not phase:
                phase = "noname"

        if not pname:
            if phase == "training":
                pname = self.get_training_network_log()
            elif phase == "test":
                pname = self.get_test_network_log()
        logging.info(" - Network log files: {}".format(pname))

        if not nlname:
            if phase == "training":
                nlname = self.get_training_label()
            elif phase == "test":
                nlname = self.get_test_label()
        logging.info(" - Network label files: {}".format(nlname))

        if not timestamp:
            timestamp = self.get_timestamp()

        logging.info(" - Making network dataset")
        if pname and nlname:
            logging.info("  => Running the packet reader to load packets at {} with {}".format(pname, nlname))
            steps = self.packet_reader.run(pname, nlname)
            pkts = self.packet_reader.get_packets()
            logging.info("  => Extracting the packet features")

            self.packet_feature_extractor.run(pkts)
            packets = self.packet_feature_extractor.get_packets()
            logging.info("  => # of packets: {}".format(len(packets)))

            logging.info("  => Running the network window manager to generate windows at {} with {}".format(pname, nlname))
            self.network_window_manager.run(packets)
            network_windows = self.network_window_manager.get_windows()
            logging.info("  => Extracting the flow features")
            self.flow_feature_extractor.run(network_windows)
            windows = self.flow_feature_extractor.get_windows()
            logging.info("  => # of windows: {}".format(len(windows)))
        return packets, windows, steps

    def quit(self):
        logging.info(" - Quitting the feature extractor")
        pass

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-p", "--network-log", metavar="<pcap filename>", help="Pcap filename", type=str, required=True)
    parser.add_argument("-q", "--network-label-file", metavar="<network label filename>", help="Network lable filename", type=str, required=True)
    parser.add_argument("-o", "--output", metavar="<output filename prefix>", help="Output filename prefix", type=str, default="noname")
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    if not check_file_availability(args.network_log):
        logging.error("The network log file ({}) does not exist.".format(network_log))
        sys.exit(1)

    if not check_file_availability(args.network_label_file):
        logging.error("The network label file ({}) does not exist.".format(network_label_file))
        sys.exit(1)
    
    pname = args.network_log
    nlname = args.network_label_file

    conf = load_configuration_file(args.config, "..")
    c = conf.get("feature_extractor", None)
    fe = FeatureExtractor(None, c)
    logging.debug("pname: {}".format(pname))
    logging.debug("nlname: {}".format(nlname))
    fe.run(pname=pname, nlname=nlname)
    fe.packet_feature_extractor.output(odir=".", ofprefix="mirai", interface="noname", timestamp=time.time())
    fe.flow_feature_extractor.output(odir=".", ofprefix="mirai", interface="noname", timestamp=time.time())

if __name__ == "__main__":
    main()
