import os, sys, argparse, logging
import yaml, json, time
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.mutils import init_metrics
from modules.module import Module

class ResultReporter(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize ResultReporter")
        super().__init__(core, conf)
        
        self.metrics = {}
        init_metrics(self)

        self.windows = None
        self.steps = None
        self.algorithms = None

        self.values = {}

    def set_steps(self, steps):
        self.steps = steps

    def set_algorithms(self, anames):
        self.algorithms = anames

    def initialize_results(self, steps, anames):
        metrics = self.metrics

        for m in metrics:
            metric = metrics[m]
            mname = metric.get_name()
            self.values[mname] = {}
            
            for step in steps:
                self.values[mname][step] = {}

                for aname in anames:
                    self.values[mname][step][aname] = metric.get_init_value()

    def add_metric(self, metric):
        self.metrics[metric.get_name()] = metric
        logging.debug("Metric {} is loaded".format(metric.get_name()))

    def run(self):
        logging.info("Running the result reporter")
        metrics = self.metrics
        windows = self.get_windows(phase="test")
        steps = self.steps = self.get_steps()
        algorithms = self.algorithms = self.get_algorithms()
        anames = []
        for aname in algorithms:
            anames.append(aname)

        if windows and steps and algorithms:
            self.initialize_results(steps, anames) 

        for m in metrics:
            metric = metrics[m]
            for step in steps:
                for aname in algorithms:
                    metric.evaluate(windows, step, algorithms[aname])

        self.report()
    
    def report(self):
        print (">>> Result of Anomaly Detection <<<")
        num = 0
        steps = self.steps
        anames = self.algorithms
        metrics = self.metrics
        for step in steps:
            num += 1
            index = 0
            print ("{}. {}".format(num, step.title()))
            for aname in anames:
                index += 1
                print (" {}) {}".format(index, aname))
                for m in metrics:
                    metric = metrics[m]
                    metric.print(step, aname)
                self.output(step, aname)
            print ("\n")
        ofname = self.get_output_filename()
        self.write_result(ofname)

    def output(self, step, aname):
        windows = self.get_windows(phase="test")
        prefix = self.get_output_file_prefix()
        ofname = "{}-{}-{}.csv".format(prefix, step, aname)
        features = windows[0].get_feature_names()
        features.append("attack_flag_labeled")
        features.append("attack_flag_prob")
        with open(ofname, "w") as of:
            fnames = ','.join(features)
            of.write("{}\n".format(fnames))
            for window in windows:
                code = list(window.get_code())
                code.append(window.get_attack_flag_labeled(step, aname))
                code.append(window.get_attack_prob(step, aname))
                line = ','.join(map(str, code))
                of.write("{}\n".format(line))

    def write_result(self, ofname):
        steps = self.steps
        anames = self.algorithms
        metrics = self.metrics
        with open(ofname, "w") as of:
            idx = 0
            for step in steps:
                idx += 1
                of.write("{}. {}\n".format(idx, step.title()))
                of.write("metric")
                for aname in anames:
                    of.write(",{}".format(aname))
                of.write("\n")
                for m in metrics:
                    metric = metrics[m]
                    of.write(metric.get_name())
                    for aname in anames:
                        of.write(",{}".format(metric.get_value(step, aname)))
                    of.write("\n")
                of.write("\n")
                of.write("\n")

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
