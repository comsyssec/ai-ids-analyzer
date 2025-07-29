import os, sys, argparse, logging
import yaml, json
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from definitions.network_window import NetworkWindow
from definitions.packet import Packet
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.etc import process_error
from modules.module import Module

class DatasetHandler(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize DatasetHandler")
        super().__init__(core, conf)

    def run(self, pname=None, fname=None, phase=None):
        logging.info("Running the dataset_handler")
        steps = ["all"]

        if not phase:
            phase = "noname"

        if not pname:
            if phase == "training":
                pname = self.get_training_packet_dataset()
            elif phase == "test":
                pname = self.get_test_packet_dataset()
        logging.info(" - Packet dataset files: {}".format(pname))

        if not fname:
            if phase == "training":
                fname = self.get_training_flow_dataset()
            elif phase == "test":
                fname = self.get_test_flow_dataset()
        logging.info(" - Flow dataset files: {}".format(fname))

        logging.info(" - Making network dataset")
        packets, windows = None, None
        if pname:
            packets = []
            logging.info("  => Loading packets from {}".format(pname))

            logging.info("  => # of packets: {}".format(len(packets)))

        if fname:
            windows = []
            logging.info("  => Loading windows from {}".format(fname))

            services = {}
            flags = {}

            with open(fname, "r") as f:
                features = f.readline().strip().split(",")
                for line in f:
                    window = NetworkWindow()
                    tmp = line.strip().split(",")
                    for idx in range(len(features)):
                        key = features[idx]
                        value = tmp[idx]
                        if key == "window_start":
                            value = float(value)
                            window.set_window_start_time(value)
                        elif key == "window_end":
                            value = float(value)
                            window.set_window_end_time(value)
                        elif key == "protocol":
                            if value == "tcp":
                                value = 6
                            elif value == "udp":
                                value = 17
                            elif value == "icmp":
                                value = 1
                            else:
                                try:
                                    value = int(value)
                                except:
                                    value = -1
                            window.set_protocol(value)
                        elif key == "src_ip_addr":
                            window.set_saddr(value)
                        elif key == "src_port":
                            try:
                                value = int(value)
                            except:
                                value = -1
                            window.set_sport(value)
                        elif key == "dst_ip_addr":
                            window.set_daddr(value)
                        elif key == "dst_port":
                            try:
                                value = int(value)
                            except:
                                value = -1
                            window.set_dport(value)
                        elif key == "attack_flag":
                            value = int(value)
                            window.set_attack_flag(value)
                        elif key == "attack_step":
                            window.set_attack_step(value)
                            if value not in steps:
                                if value not in ["benign", "-"]:
                                    steps.append(value)
                        elif key == "attack_name":
                            window.set_attack_name(value)
                        else:
                            if key == "service":
                                if value not in services:
                                    services[value] = len(services) + 1
                                value = services[value]
                            elif key == "flag":
                                if value not in flags:
                                    flags[value] = len(flags) + 1
                                value = flags[value]
                            value = float(value)
                            window.add_feature_value(key, value)
                    windows.append(window)
            logging.info("  => # of windows: {}".format(len(windows)))
        return packets, windows, steps

    def quit(self):
        logging.info(" - Quitting the dataset handler")
        pass

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-p", "--packet-dataset", metavar="<packet dataset filename>", help="Packet dataset filename", type=str, default=None)
    parser.add_argument("-f", "--flow-dataset", metavar="<flow dataset filename>", help="Flow dataset filename", type=str, default=None)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    if args.packet_dataset and not check_file_availability(args.packet_dataset):
        logging.error("The packet dataset file ({}) does not exist.".format(args.packet_dataset))
        sys.exit(1)

    if args.flow_dataset and not check_file_availability(args.flow_dataset):
        logging.error("The flow dataset file ({}) does not exist.".format(args.flow_dataset))
        sys.exit(1)
    
    conf = load_configuration_file(args.config, "..")
    c = conf.get("feature_extractor", None)
    dh = DatasetHandler(None, c)
    packets, windows = dh.run(pname=args.packet_dataset, fname=args.flow_dataset)

if __name__ == "__main__":
    main()
