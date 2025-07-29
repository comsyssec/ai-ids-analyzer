import os, sys, argparse, logging
import yaml
from iutils.etc import camel_code

def prepare_features(dname):
    pdir = "{}/packet".format(dname)
    fdir = "{}/flow".format(dname)

    pnames = []
    fnames = []

    pfeatures = [f for f in os.listdir(pdir) if f.endswith(".py")]
    ffeatures = [f for f in os.listdir(fdir) if f.endswith(".py")]

    for f in pfeatures:
        pnames.append(f.split(".")[0])

    for f in ffeatures:
        fnames.append(f.split(".")[0])

    return pnames, fnames

def prepare_algorithms(aname):
    adir = "{}".format(aname)

    anames = []
    aalgorithms = [f for f in os.listdir(adir) if f.endswith(".py") and f != "algorithm.py"]
    
    for f in aalgorithms:
        anames.append(f.split(".")[0])

    return anames

def prepare_metrics(mname):
    mdir = "{}".format(mname)

    mnames = []
    metrics = [m for m in os.listdir(mdir) if m.endswith(".py") and m != "metric.py"]
    
    for m in metrics:
        mnames.append(m.split(".")[0])

    return mnames

def prepare_datasets(dname):
    ddir = "{}".format(dname)

    dnames = []
    ddatasets = [d for d in os.listdir(ddir) if os.path.isdir("{}/{}".format(ddir, d))]
    
    for d in ddatasets:
        dnames.append("{}/{}".format(ddir, d))

    return dnames

def make_config(dnames, pnames, fnames, anames, mnames):
    conf = {}
    modules = ["general", "feature_extractor", "model_manager", "result_reporter"]

    for d in dnames:
        dname = d.strip().split("/")[1].strip()
        ofname = "{}.yaml".format(dname)

        for m in modules:
            conf[m] = {}
            conf[m]["name"] = m

        conf["general"]["name"] = "ids-tester"
        conf["general"]["timeout"] = 600
        conf["general"]["dataset_type"] = "csv"
        conf["general"]["training_packet_dataset"] = "{}/training-packet.csv".format(d)
        conf["general"]["training_flow_dataset"] = "{}/training-flow.csv".format(d)
        conf["general"]["training_network_log"] = "{}/training.pcap".format(d)
        conf["general"]["training_label"] = "{}/training.label".format(d)
        conf["general"]["test_packet_dataset"] = "{}/test-packet.csv".format(d)
        conf["general"]["test_flow_dataset"] = "{}/test-flow.csv".format(d)
        conf["general"]["test_network_log"] = "{}/test.pcap".format(d)
        conf["general"]["test_label"] = "{}/test.label".format(d)
        conf["general"]["prefix"] = dname
        conf["general"]["output"] = "output-{}.csv".format(dname)

        conf["feature_extractor"]["features"] = {}

        # packet features
        conf["feature_extractor"]["features"]["packet"] = {}
        for p in pnames:
            conf["feature_extractor"]["features"]["packet"][p] = True

        # flow features
        conf["feature_extractor"]["features"]["flow"] = {}
        for f in fnames:
            conf["feature_extractor"]["features"]["flow"][f] = True

        # window_length and sliding_window_interval are in milliseconds
        conf["feature_extractor"]["network_window_manager"] = {}
        conf["feature_extractor"]["network_window_manager"]["name"] = "network_window_manager"
        conf["feature_extractor"]["network_window_manager"]["window_length"] = 1000
        conf["feature_extractor"]["network_window_manager"]["sliding_window"] = True
        conf["feature_extractor"]["network_window_manager"]["sliding_window_interval"] = 100

        # algorithms
        conf["model_manager"]["steps"] = True
        conf["model_manager"]["algorithms"] = {}
        for a in anames:
            conf["model_manager"]["algorithms"][a] = True

        # metrics
        conf["result_reporter"]["metrics"] = {}
        for m in mnames:
            conf["result_reporter"]["metrics"][m] = True

        with open(ofname, "w") as of:
            yaml.dump(conf, of, sort_keys=False)

def make_initializer(pnames, fnames, anames, mnames):
    with open("iutils/futils.py", "w") as of:
        of.write("import os, sys, logging\n")
        of.write("import pathlib\n")
        of.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        of.write("root_directory = os.path.abspath(\"{}/..\".format(fpath))\n")
        of.write("if root_directory not in sys.path:\n")
        of.write("    sys.path.insert(0, root_directory)\n")
        
        for f in pnames:
            of.write("from features.packet.{} import {}\n".format(f, camel_code(f)))

        for f in fnames:
            of.write("from features.flow.{} import {}\n".format(f, camel_code(f)))

        of.write("\n")
        of.write("def init_packet_features(feature_extractor):\n")
        names = pnames
        if len(names) > 0:
            for f in names:
                of.write("    feature_extractor.add_feature({}(\"{}\"))\n".format(camel_code(f), f))
        else:
            of.write("    pass\n")

        of.write("\n")
        of.write("def init_flow_features(feature_extractor):\n")
        names = fnames
        if len(names) > 0:
            for f in names:
                of.write("    feature_extractor.add_feature({}(\"{}\"))\n".format(camel_code(f), f))
        else:
            of.write("    pass\n")

        of.write("\n")

    with open("iutils/autils.py", "w") as of:
        of.write("import os, sys, logging\n")
        of.write("import pathlib\n")
        of.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        of.write("root_directory = os.path.abspath(\"{}/..\".format(fpath))\n")
        of.write("if root_directory not in sys.path:\n")
        of.write("    sys.path.insert(0, root_directory)\n")
        
        for a in anames:
            of.write("from algorithms.{} import {}\n".format(a, camel_code(a)))

        of.write("\n")
        of.write("def init_algorithms(model_manager):\n")
        names = anames
        if len(names) > 0:
            for a in names:
                of.write("    model_manager.add_algorithm({}(\"{}\"))\n".format(camel_code(a), a))
        else:
            of.write("    pass\n")

        of.write("\n")

    with open("iutils/mutils.py", "w") as of:
        of.write("import os, sys, logging\n")
        of.write("import pathlib\n")
        of.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        of.write("root_directory = os.path.abspath(\"{}/..\".format(fpath))\n")
        of.write("if root_directory not in sys.path:\n")
        of.write("    sys.path.insert(0, root_directory)\n")
        
        for m in mnames:
            of.write("from metrics.{} import {}\n".format(m, camel_code(m)))

        of.write("\n")
        of.write("def init_metrics(result_reporter):\n")
        names = mnames
        if len(names) > 0:
            for m in names:
                of.write("    result_reporter.add_metric({}(\"{}\"))\n".format(camel_code(m), m))
        else:
            of.write("    pass\n")

        of.write("\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--algorithms", help="Algorithm directory", type=str, default="algorithms")
    parser.add_argument("-d", "--datasets", help="Dataset directory", type=str, default="data")
    parser.add_argument("-f", "--features", help="Feature directory", type=str, default="features")
    parser.add_argument("-m", "--metrics", help="Metric directory", type=str, default="metrics")
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", default="INFO", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()

    logging.basicConfig(level=args.log)

    if not os.path.exists(args.algorithms):
        logging.error ("Invalid algorithm directory. Please insert the correct algorithm directory")
        sys.exit(1)

    if not os.path.exists(args.datasets):
        logging.error ("Invalid dataset directory. Please insert the correct dataset directory")
        sys.exit(1)

    if not os.path.exists(args.features):
        logging.error ("Invalid feature directory. Please insert the correct feature directory")
        sys.exit(1)

    if not os.path.exists(args.metrics):
        logging.error ("Invalid metric directory. Please insert the correct metric directory")
        sys.exit(1)

    pnames, fnames = prepare_features(args.features)
    logging.debug("pnames: {}".format(pnames))
    logging.debug("fnames: {}".format(fnames))

    anames = prepare_algorithms(args.algorithms)
    logging.debug("anames: {}".format(anames))

    mnames = prepare_metrics(args.metrics)
    logging.debug("mnames: {}".format(mnames))

    dnames = prepare_datasets(args.datasets)
    logging.debug("dnames: {}".format(dnames))

    make_config(dnames, pnames, fnames, anames, mnames)
    make_initializer(pnames, fnames, anames, mnames)

    logging.info("Please check the configuration files")

if __name__ == "__main__":
    main()
