import os
import logging 

class Module:
    def __init__(self, core, conf):
        self.core = core
        self.config = conf
        logging.debug("self.config in module: {}".format(self.config))

    def run(self):
        pass

    def get_names(self):
        ret = None
        if self.core:
            ret = self.core.get_names()
        return ret

    def set_steps(self, steps):
        if self.core:
            self.core.set_steps(steps)

    def get_steps(self):
        ret = None
        if self.core:
            ret = self.core.get_steps()
        return ret

    def set_algorithms(self, algorithms):
        if self.core:
            self.core.set_algorithms(algorithms)

    def get_algorithms(self):
        ret = None
        if self.core:
            ret = self.core.get_algorithms()
        return ret

    def get_timestamp(self):
        ret = None
        if self.core:
            ret = self.core.get_timestamp()
        return ret

    def get_packets(self, phase=None):
        ret = None
        if self.core:
            ret = self.core.get_packets(phase)
        return ret

    def get_windows(self, phase=None):
        ret = None
        if self.core:
            ret = self.core.get_windows(phase)
        return ret

    def get_root_directory(self):
        ret = None
        if self.core:
            ret = self.core.get_root_directory()
        else:
            ret = os.getcwd() + "/.."
        return ret

    def get_training_packet_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_training_packet_dataset()
        return ret

    def get_training_flow_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_training_flow_dataset()
        return ret

    def get_training_network_log(self):
        ret = None
        if self.core:
            ret = self.core.get_training_network_log()
        return ret

    def get_training_label(self):
        ret = None
        if self.core:
            ret = self.core.get_training_label()
        return ret

    def get_test_packet_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_test_packet_dataset()
        return ret

    def get_test_flow_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_test_flow_dataset()
        return ret

    def get_test_network_log(self):
        ret = None
        if self.core:
            ret = self.core.get_test_network_log()
        return ret

    def get_test_label(self):
        ret = None
        if self.core:
            ret = self.core.get_test_label()
        return ret

    def set_output_directory(self, odir):
        if self.core:
            self.core.set_output_directory(odir)

    def get_output_directory(self):
        ret = None
        if self.core:
            ret = self.core.get_output_directory()
        return ret

    def set_output_file_prefix(self, ofprefix):
        if self.core:
            self.core.set_output_file_prefix(ofprefix)

    def get_output_file_prefix(self):
        ret = None
        if self.core:
            ret = self.core.get_output_file_prefix()
        return ret

    def get_output_filename(self):
        ret = None
        if self.core:
            ret = self.core.get_output_filename()
        return ret

    def add_labeled_packet_dataset(self, dpname):
        if self.core:
            self.core.add_labeled_packet_dataset(dpname)
        else:
            if not hasattr(self, "labeled_packet_dataset"):
                self.labeled_packet_dataset = []
            self.labeled_packet_dataset.append(dpname)

    def add_labeled_flow_dataset(self, dfname):
        if self.core:
            self.core.add_labeled_flow_dataset(dfname)
        else:
            if not hasattr(self, "labeled_flow_dataset"):
                self.labeled_flow_dataset = []
            self.labeled_flow_dataset.append(dfname)

    def get_labeled_packet_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_labeled_packet_dataset()
        else:
            if hasattr(self, "labeled_packet_dataset"):
                ret = self.labeled_packet_dataset
        return ret

    def get_labeled_flow_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_labeled_flow_dataset()
        else:
            if hasattr(self, "labeled_flow_dataset"):
                ret = self.labeled_flow_dataset
        return ret
