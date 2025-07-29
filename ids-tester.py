import os, sys, argparse, logging
import yaml, time
import subprocess
import signal
import warnings
from modules.feature_extractor import FeatureExtractor
from modules.dataset_handler import DatasetHandler
from modules.model_manager import ModelManager
from modules.result_reporter import ResultReporter
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file

warnings.filterwarnings("ignore", message="X does not have valid feature *")

class AIIDSAnalyzer:
    def __init__(self, conf):
        logging.info("Starting the AI-IDS-Analyzer")
        self.start_time = int(time.time())
        self.config = conf
        self.root_directory = conf["general"]["root_directory"]

        self.packet_dataset = {}
        self.flow_dataset = {}
        self.network_log = {}
        self.label = {}
        self.data_type = conf["general"].get("dataset_type", "raw")
        self.packet_dataset["training"] = conf["general"].get("training_packet_dataset", None)
        self.flow_dataset["training"] = conf["general"].get("training_flow_dataset", None)
        self.network_log["training"] = conf["general"].get("training_network_log", None)
        self.label["training"] = conf["general"].get("training_label", None)
        self.packet_dataset["test"] = conf["general"].get("test_packet_dataset", None)
        self.flow_dataset["test"] = conf["general"].get("test_flow_dataset", None)
        self.network_log["test"] = conf["general"].get("test_network_log", None)
        self.label["test"] = conf["general"].get("test_label", None)

        self.packets = {}
        self.windows = {}

        self.output_directory = None
        self.output_file_prefix = conf["general"]["prefix"]
        self.ofname = conf["general"]["output"]

        self.labeled_packet_dataset = []
        self.labeled_flow_dataset = []

        self.timestamp = int(time.time())

        self.sig = signal.SIGINT

        def signal_handler(signum, frame):
            logging.error("Stopping gracefully on capturing Ctrl+C")
            self.quit()
            sys.exit(1)
        signal.signal(self.sig, signal_handler)

        self.init_modules()
        self.run()

        self.quit()
        self.end_time = int(time.time())
        logging.info("Total elapsed time: {} s".format(self.end_time - self.start_time))

    def init_modules(self):
        conf = self.config

        # Initialize the feature extractor
        c = conf.get("feature_extractor", None)
        self.feature_extractor = FeatureExtractor(self, c)

        # Initialize the data handler
        c = conf.get("dataset_handler", None)
        self.dataset_handler = DatasetHandler(self, c)

        # Initialize the model manager
        c = conf.get("model_manager", None)
        self.model_manager = ModelManager(self, c)

        # Initialize the result reporter
        c = conf.get("result_reporter", None)
        self.result_reporter = ResultReporter(self, c)

    def run(self):
        complete_training = False
        complete_test = False

        logging.info("[AI-IDS-Analyzer] Load the dataset for training")
        if self.data_type == "raw":
            self.packets["training"], self.windows["training"], self.steps = self.feature_extractor.run(phase="training")
        elif self.data_type == "csv":
            self.packets["training"], self.windows["training"], self.steps = self.dataset_handler.run(phase="training")

        logging.info("[AI-IDS-Analyzer] Make the model based on the training set")
        if self.packets.get("training", None) or self.windows.get("training", None):
            if self.packets.get("training"):
                logging.info(" - Training packet dataset: {}".format(len(self.packets["training"])))
            if self.windows.get("training"):
                logging.info(" - Training flow dataset: {}".format(len(self.windows["training"])))
            self.model_manager.run(phase="training", steps=self.steps)
            complete_training = True

        logging.info("[AI-IDS-Analyzer] Load the dataset for testing")
        if self.data_type == "raw":
            self.packets["test"], self.windows["test"], _ = self.feature_extractor.run(phase="test")
        elif self.data_type == "csv":
            self.packets["test"], self.windows["test"], _ = self.dataset_handler.run(phase="test")

        logging.info("[AI-IDS-Analyzer] Test the model based on the test set")
        if self.packets.get("test", None) or self.windows.get("test", None):
            if self.packets.get("test"):
                logging.info(" - Test packet dataset: {}".format(len(self.packets["test"])))
            if self.windows.get("test"):
                logging.info(" - Test flow dataset: {}".format(len(self.windows["test"])))
            self.model_manager.run(phase="test")
            complete_test = True

        logging.info("[AI-IDS-Analyzer] Report the performance results")
        if complete_training and complete_test:
            self.result_reporter.set_steps(self.steps)
            self.result_reporter.run()

    def quit(self):
        logging.info("Quitting the entire processes")
        self.feature_extractor.quit()

    def set_steps(self, steps):
        self.steps = steps

    def get_steps(self):
        return self.steps

    def set_algorithms(self, algorithms):
        self.algorithms = algorithms

    def get_algorithms(self):
        return self.algorithms

    def get_root_directory(self):
        return self.root_directory

    def get_labeled_packet_dataset(self):
        return self.labeled_packet_dataset

    def get_labeled_flow_dataset(self):
        return self.labeled_flow_dataset

    def set_output_directory(self, odir):
        self.output_directory = odir

    def get_output_directory(self):
        return self.output_directory

    def set_output_file_prefix(self, ofprefix):
        self.output_file_prefix = ofprefix

    def get_output_filename(self):
        return self.ofname

    def get_output_file_prefix(self):
        return self.output_file_prefix

    def get_training_packet_dataset(self):
        return self.packet_dataset["training"]

    def get_training_flow_dataset(self):
        return self.flow_dataset["training"]

    def get_training_network_log(self):
        return self.network_log["training"]

    def get_training_label(self):
        return self.label["training"]

    def get_test_packet_dataset(self):
        return self.packet_dataset["test"]

    def get_test_flow_dataset(self):
        return self.flow_dataset["test"]

    def get_test_network_log(self):
        return self.network_log["test"]

    def get_test_label(self):
        return self.label["test"]

    def get_timestamp(self):
        return self.timestamp

    def get_packets(self, phase=None):
        if not phase:
            return self.packets
        else:
            return self.packets.get(phase, None)

    def get_windows(self, phase=None):
        if not phase:
            return self.windows
        else:
            return self.windows.get(phase, None)

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, default="config.yaml")
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, ".")

    logging.debug("configuration: {}".format(conf))
    AIIDSAnalyzer(conf)

if __name__ == "__main__":
	main()
