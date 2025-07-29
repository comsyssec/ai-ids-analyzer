import os, sys, argparse, logging
import time
import threading
import copy
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.autils import init_algorithms
from definitions.window_set import WindowSet
from modules.module import Module
from sklearn import metrics
from tqdm import tqdm

usleep = lambda x: time.sleep(x/1000000.0)
THREAD_USLEEP_TIME = 30000
WAITING_USLEEP_TIME = 10000
PROCESS_TIMEOUT = 3/1000000.0
OFFSET = 0.2

class ModelManager(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize ModelManager")
        super().__init__(core, conf)
        
        self.algorithms = {}
        init_algorithms(self)

        self.training_set = WindowSet()
        self.training_packets = 0
        self.test_set = WindowSet()
        self.test_packets = 0
    
        self.detections = 0
        self.total_windows = 0

        self.learning_time = {}

        self.enable_steps = conf.get("steps", False)
        self.steps = None

        self.names = []
        self.amodels = {}
        self.wlst = []
        algorithms = self.config.get("algorithms", None)
        for a in algorithms:
            if algorithms[a]:
                self.names.append(a)
                self.amodels[a] = self.algorithms[a]
        self.set_algorithms(self.amodels)
        logging.debug("algorithms: {}".format(self.names))

    def run(self, phase=None, steps=None):
        logging.info("Running the model manager")
        if steps:
            if self.enable_steps:
                self.steps = steps
            else:
                self.steps = ["all"]
            #self.initialize_results(self.steps)
            self.set_steps(self.steps)
        steps = self.steps

        if not phase:
            logging.error("No phase is specified")
            sys.exit(1)

        windows = self.get_windows(phase=phase)
        if not windows:
            logging.error("No window is assigned")
            sys.exit(1)

        for step in steps:
            for aname in self.names:
                self.algorithms[aname].set_num_of_windows(is_training=(phase=="training"), num=len(windows))

        if phase == "training":
            logging.info("  - Training the model")
            start = int(time.time())
            for window in tqdm(windows, leave=True, colour='magenta'):
                self.learning(window=window)
            end = int(time.time())
            for step in steps:
                if sum(self.training_set.get_labels(step)) > 0:
                    if step not in self.steps:
                        self.steps.append(step)
                else:
                    if step in self.steps:
                        self.steps.remove(step)
            self.learning(window=None)
        elif phase == "test":
            logging.info("  - Testing the model")
            self.total_windows = len(windows)
            for window in tqdm(windows, leave=True, colour='magenta'):
                self.detection(window=window)
            #self.detection(window=None)

            #logging.info("Reporting the result")
            #self.report()

    def add_algorithm(self, algorithm):
        self.algorithms[algorithm.get_name()] = algorithm
        logging.debug("Algorithm {} is loaded".format(algorithm.get_name()))

    def learning(self, window):
        steps = self.steps
        if window:
            self.training_packets += window.get_num_of_packets("both")
            self.training_set.add_window(window)

        else:
            logging.info("Generating the model based on the training set")
            dataset = self.training_set.get_dataset()
            logging.info("  - # of Samples in Dataset: {}".format(len(dataset)))
            logging.debug("Dataset ({}): {}".format(len(dataset), dataset))
            idx = 0
            remove = []
            for step in steps:
                idx += 1
                logging.info("{}) Generating the {} models".format(idx, step))
                if self.names:
                    for aname in self.names:
                        logging.info(" - Building the {} model based on {}".format(step, aname))
                        before = time.time()
                        self.algorithms[aname].learning(self.training_set, step)
                        after = time.time()
                        if step not in self.learning_time:
                            self.learning_time[step] = {}
                        self.learning_time[step][aname] = round(after - before, 2)
                        logging.info("  => Model created for {} s".format(self.learning_time[step][aname]))

            logging.info("Finishing the model creation based on the training set")

    def detection(self, window):
        logging.debug("Detecting the anomalies on windows")
        steps = self.steps
        if window:
            aresult = None

            num = 0
            for step in steps:
                num += 1
                for aname in self.names:
                    logging.debug("  - {} detection based on {}".format(step, aname))
                    self.wlst.append(window)
                    start = time.time()
                    result = self.algorithms[aname].detection(window, step)
                    end = time.time()
                    logging.debug("  - {} detection time: {} s".format(step, end - start))

                    if result:
                        aresult, aprob = result
                        for i in range(len(aresult)):
                            self.wlst[i].set_attack_flag_labeled(step, aname, aresult[i])
                            self.wlst[i].set_attack_prob(step, aname, aprob[i])
                            if aresult[i] == 1:
                                logging.debug("{}) The Window is identified as an anomalous one".format(aname))
                            ltime = self.learning_time[step][aname]
                            self.wlst[i].set_learning_time(step, aname, ltime)
                            dtime = (end - start) / len(aresult)
                            self.wlst[i].set_detection_time(step, aname, dtime)
                            self.wlst = []

            logging.debug("Finishing the detection")

    def report(self, ofname=None):
        self.print_result()
        if not ofname:
            ofname = self.get_output_filename()
        if ofname:
            self.write_result(ofname)

    def print_result(self):
        print (">>> Result of Anomaly Detection <<<")

        steps = self.steps
        num = 0
        for step in steps:
            num += 1
            index = 0
            print ("{}. {}".format(num, step.title()))
            for aname in self.names:
                index += 1
                print ("{}) {}".format(index, aname))
                print ("  - Accuracy: {}".format(self.accuracy[step][aname]))
                print ("  - Precision: {}".format(self.precision[step][aname]))
                print ("  - Recall: {}".format(self.recall[step][aname]))
                print ("  - F1: {}".format(self.f1[step][aname]))
                print ("  - # of Training Samples: {}".format(len(self.training_set.get_dataset())))
                print ("  - # of Training {} Samples: {}".format(step.title(), self.training_set.get_num_of_types(step)))
                print ("  - # of Training Packets: {}".format(self.training_packets))
                print ("  - # of Test Samples: {}".format(len(self.test_labels[step])))
                print ("  - # of Test Packets: {}".format(self.test_packets))
                print ("    # of Benign windows: {}".format(self.num_of_benign_windows))
                print ("    # of {} windows: {}".format(step.title(), self.num_of_windows[step]))
                print ("  - True Positive: {}".format(self.true_positive[step][aname]))
                print ("  - True Negative: {}".format(self.true_negative[step][aname]))
                print ("  - False Positive: {}".format(self.false_positive[step][aname]))
                print ("  - False Negative: {}".format(self.false_negative[step][aname]))
                print ("  - Learning Time: {} ms".format(self.learning_time[step][aname] * 1000))
                print ("  - Averaged Detection Time: {} ms".format(self.detection_time[step][aname] / len(self.test_labels[step]) * 1000))
                
                if hasattr(self.algorithms[aname], "classifier"):
                    if step in self.algorithms[aname].classifier:
                        if hasattr(self.algorithms[aname].classifier[step], "feature_importances_"):
                            fnames = self.training_set.get_feature_names()
                            #print ("  - Feature Name: {}".format(fnames))
                            lst = self.algorithms[aname].classifier[step].feature_importances_
                            #print ("  - Feature Importance: {}".format(lst))
                            top5_idx = []
                            while len(top5_idx) < 5:
                                v = -1
                                i = -1
                                for idx in range(len(lst)):
                                    if idx not in top5_idx:
                                        if lst[idx] > v:
                                            v = lst[idx]
                                            i = idx
                                top5_idx.append(i)

                            top5 = []
                            for idx in top5_idx:
                                top5.append(fnames[idx])
                            print ("  - Top 5 Features: {}".format(','.join(top5)))

                    print ("")


    def write_result(self, ofname):
        steps = self.steps
        with open(ofname, "w") as of:
            idx = 0
            for step in steps:
                idx += 1
                of.write("{}. {}\n".format(idx, step.title()))
                of.write("metric")
                for aname in self.names:
                    of.write(",{}".format(aname))
                of.write("\n")
                of.write("accuracy")
                for aname in self.names:
                    of.write(",{}".format(self.accuracy[step][aname]))
                of.write("\n")
                of.write("precision")
                for aname in self.names:
                    of.write(",{}".format(self.precision[step][aname]))
                of.write("\n")
                of.write("recall")
                for aname in self.names:
                    of.write(",{}".format(self.recall[step][aname]))
                of.write("\n")
                of.write("f1")
                for aname in self.names:
                    of.write(",{}".format(self.f1[step][aname]))
                of.write("\n")
                of.write("training_samples")
                for aname in self.names:
                    of.write(",{}".format(len(self.training_set.get_dataset())))
                of.write("\n")
                of.write("training_{}_samples".format(step))
                for aname in self.names:
                    of.write(",{}".format(self.training_set.get_num_of_types(step)))
                of.write("\n")
                of.write("training_packets")
                for aname in self.names:
                    of.write(",{}".format(self.training_packets))
                of.write("\n")
                of.write("test_samples")
                for aname in self.names:
                    of.write(",{}".format(len(self.test_labels[step])))
                of.write("\n")
                of.write("test_packets")
                for aname in self.names:
                    of.write(",{}".format(self.test_packets))
                of.write("\n")
                of.write("benign_windows")
                for aname in self.names:
                    of.write(",{}".format(self.num_of_benign_windows))
                of.write("\n")
                of.write("{}_windows".format(step))
                for aname in self.names:
                    of.write(",{}".format(self.num_of_windows[step]))
                of.write("\n")
                of.write("true_positive")
                for aname in self.names:
                    of.write(",{}".format(self.true_positive[step][aname]))
                of.write("\n")
                of.write("true_negative")
                for aname in self.names:
                    of.write(",{}".format(self.true_negative[step][aname]))
                of.write("\n")
                of.write("false_positive")
                for aname in self.names:
                    of.write(",{}".format(self.false_positive[step][aname]))
                of.write("\n")
                of.write("false_negative")
                for aname in self.names:
                    of.write(",{}".format(self.false_negative[step][aname]))
                of.write("\n")
                of.write("learning_time")
                for aname in self.learning_time[step]:
                    of.write(",{}".format(self.learning_time[step][aname]))
                of.write("\n")
                of.write("detection_time")
                for aname in self.detection_time[step]:
                    of.write(",{}".format(self.detection_time[step][aname]))
                of.write("\n")
                of.write("\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str)

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, "..")
    c = conf.get("model_manager", None)
    mm = ModelManager(None, c)

if __name__ == "__main__":
    main()
