from definitions.network_window import NetworkWindow
import numpy as np
import logging
import copy
import time
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class WindowSet:
    def __init__(self):
        self.windows = []
        self.revised = {}
        self.dataset = {}
        self.labels = {}
        self.standard = None
        self.minmax = None

    def add_window(self, window):
        self.windows.append(window)

    def get_windows(self):
        return self.windows

    def get_windows_length(self):
        return len(self.windows)

    def get_feature_names(self):
        ret = None
        if len(self.windows) > 0:
            ret = self.windows[0].get_feature_names()
        return ret

    def get_dataset(self, step=None, select=None, scaler="standard"):
        ret = None

        if step not in self.dataset:
            dataset = []
            benign = []
            anomalous = []
        
            if step:
                for w in self.windows:
                    if w.get_label(step) == 1:
                        anomalous.append(w)
                    else:
                        benign.append(w)

                if select == "benign":
                    self.revised[step] = benign
                elif select == "anomalous":
                    self.revised[step] = anomalous
                else:
                    self.revised[step] = benign + anomalous
                for w in self.revised[step]:
                    dataset.append(w.get_code())

            else:
                for w in self.windows:
                    dataset.append(w.get_code())

            self.dataset[step] = np.array(dataset)

            scaler = StandardScaler().fit(self.dataset[step])
            scaled = scaler.transform(self.dataset[step])
            self.standard = scaler, scaled

            scaler = MinMaxScaler().fit(self.dataset[step])
            scaled = scaler.transform(self.dataset[step])
            self.minmax = scaler, scaled

        if scaler == "standard":
            ret = self.standard
        elif scaler == "minmax":
            ret = self.minmax
        else:
            ret = self.standard
        return ret

    def get_num_of_types(self, step):
        num = 0
        for w in self.windows:
            if w.get_label(step) == 1:
                num += 1
        return num

    def get_labels(self, step, dl=False):
        ret = None
        if step not in self.labels:
            ml_labels = []
            dl_labels = []

            if step in self.revised:
                for w in self.revised[step]:
                    label = w.get_label(step)
                    ml_labels.append(label)
                    dl_labels.append([label])
            else:
                for w in self.windows:
                    label = w.get_label(step)
                    ml_labels.append(label)
                    dl_labels.append([label])

            self.labels[step] = {}
            self.labels[step]["ml"] = np.array(ml_labels)
            self.labels[step]["dl"] = np.array(dl_labels)
        
        if dl == True:
            ret = self.labels[step]["dl"]
        else:
            ret = self.labels[step]["ml"]
        return ret

    def print(self):
        print (">>>>> Windows Information <<<<<")
        for w in self.windows:
            #print ("{}) {}".format(w.get_serial_number(), w.get_code()))
            print ("{}) Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(w.get_serial_number(), w.get_window_start_time(), w.get_window_end_time(), w.get_num_of_packets("forward"), w.get_num_of_packets("backward")))

    def store(self, sfname, training):
        with open(sfname, "w") as of:
            windows = self.get_windows()
            #if training:
            #    windows = balancing(windows)
            fnames = windows[0].get_feature_names()

            for f in fnames[:-1]:
                of.write("{}, ".format(f))
            of.write("{}: start_time, end_time: label\n".format(fnames[-1]))

            for w in windows:
                [code] = w.get_code()
                start_time = w.get_window_start_time()
                end_time = w.get_window_end_time()

                for c in code[:-1]:
                    of.write("{}, ".format(c))
                of.write("{}".format(code[-1]))
                label = w.get_label()
                of.write(": {}, {}: {}\n".format(start_time, end_time, label))

def balancing(windows):
    num = {}
    num[0] = 0 # benign
    num[1] = 0 # action
    num[2] = 0 # infection
    num[3] = 0 # reconnaissance

    for w in windows:
        label = w.get_best_label()
        num[label] += 1

    if num[0] == 0 or num[1] == 0 or num[2] == 0 or num[3] == 0:
        logging.error("The training set should be replayed: benign: {} / action: {} / infection: {} / reconnaissance: {}".format(num[0], num[1], num[2], num[3]))
        sys.exit(1)

    mval = num[0]
    for i in range(4):
        if mval < num[i]:
            mval = num[i]

    win = {}
    left = {}

    for i in range(4):
        win[i] = []
        left[i] = mval - num[i]

    while left[0] > 0 or left[1] > 0 or left[2] > 0 or left[3] > 0:
        for w in windows:
            label = w.get_best_label()

            if left[label] > 0:
                if left[label] < num[label]:
                    coin = random.random()
                    if coin < 0.7:
                        win[label].append(copy.deepcopy(w))
                        left[label] -= 1
                else:
                    win[label].append(copy.deepcopy(w))
                    left[label] -= 1

    windows = windows + win[0] + win[1] + win[2] + win[3]
    windows = sorted(windows, key=lambda x: x.get_window_start_time())

    revised = {}
    for i in range(4):
        revised[i] = 0

    for w in windows:
        label = w.get_best_label()
        revised[label] += 1

    logging.info("Revised number of samples: benign: {}, action: {}, infection: {}, reconnaissance: {}".format(revised[0], revised[1], revised[2], revised[3]))
    return windows

