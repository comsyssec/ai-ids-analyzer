import os, sys, argparse, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import camel_code

def generate_template(ftype, name):
    fname = "{}/features/{}/{}.py".format(root_directory, ftype, name)

    with open(fname, "w") as f:
        f.write("import os, sys, logging\n")
        f.write("import pathlib\n")
        f.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        f.write("root_directory = os.path.abspath(\"{}/../..\".format(fpath))\n")
        f.write("from features.feature import Feature\n\n")
        f.write("class {}(Feature):\n".format(camel_code(name)))
        f.write("    def __init__(self, name):\n")
        f.write("        super().__init__(name, \"{}\")\n\n".format(ftype))
        f.write("    # Please implement the following function\n")
        f.write("    # The variable `val` should contain the result value\n")
        if ftype == "flow" or ftype == "transition":
            f.write("    def extract_feature(self, window):\n")
        elif ftype == "packet":
            f.write("    def extract_feature(self, packet):\n")
        elif ftype == "host":
            f.write("    def extract_feature(self, hlog):\n")
        else:
            f.write("    def extract_feature(self, window):\n")
        f.write("        # TODO: Implement the procedure to extract the feature\n")
        f.write("\n")
        f.write("\n")
        if ftype == "flow" or ftype == "transition":
            f.write("        window.add_feature_value(self.get_name(), val)\n")
        elif ftype == "packet":
            f.write("        packet.add_feature_value(self.get_name(), val)\n")
        elif ftype == "host":
            f.write("        hlog.add_feature_value(self.get_name(), val)\n")
        else:
            f.write("        window.add_feature_value(self.get_name(), val)\n")
        f.write("        logging.debug('{}: {}'.format(self.get_name(), val))\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", required=True, help="Feature type (packet/flow/host/transition)", type=str, choices=["packet", "flow", "host", "transition"])
    parser.add_argument("-n", "--name", required=True, help="Feature name", type=str)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    ftype = args.type
    name = args.name

    fname = "../features/{}/{}.py".format(ftype, name)

    if os.path.exists(fname):
        print ("The same name of the feature exists. Please insert another name for the feature to be defined")
        sys.exit(1)

    generate_template(ftype, name)

if __name__ == "__main__":
    main()
