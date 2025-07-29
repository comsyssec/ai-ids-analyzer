import os, sys, argparse, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import camel_code

def generate_template(name):
    fname = "{}/metrics/{}.py".format(root_directory, name)

    with open(fname, "w") as f:
        f.write("import os, sys, logging\n")
        f.write("import pathlib\n")
        f.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        f.write("root_directory = os.path.abspath(\"{}/../..\".format(fpath))\n")
        f.write("from metrics.metric import Metric\n\n")
        f.write("class {}(Metric):\n".format(camel_code(name)))
        f.write("    def __init__(self, name):\n")
        f.write("        super().__init__(name)\n\n")
        f.write("    # Please implement the following functions\n")
        f.write("    def get_init_value(self):\n")
        f.write("        # TODO: Implement the following statement to display the result\n")
        f.write("        return \n")
        f.write("\n")
        f.write("\n")
        f.write("    def get_unit(self):\n")
        f.write("        # TODO: Implement the following statement to display the result\n")
        f.write("        return \n")
        f.write("\n")
        f.write("\n")
        f.write("    def evaluate(self, windows, step, amodel):\n")
        f.write("        # TODO: Implement the procedure to evaluate the model\n")
        f.write("        return val\n")
        f.write("\n")
        f.write("\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, help="Metric name", type=str)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    name = args.name

    fname = "../metrics/{}.py".format(name)

    if os.path.exists(fname):
        print ("The same name of the metric exists. Please insert another name for the metric to be defined")
        sys.exit(1)

    generate_template(name)

if __name__ == "__main__":
    main()
