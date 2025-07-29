import os, sys, argparse, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import camel_code

def generate_template(name):
    fname = "{}/algorithms/{}.py".format(root_directory, name)

    with open(fname, "w") as f:
        f.write("import sys\n")
        f.write("import logging\n")
        f.write("from algorithms.algorithm import Algorithm\n\n")
        f.write("class {}(Algorithm):\n".format(camel_code(name)))
        f.write("    def __init__(self, name):\n")
        f.write("        super().__init__(name)\n\n")
        f.write("    # Please implement the following functions\n")
        f.write("    # Concerning dataset, refer to the class TrainingSet\n")
        f.write("    def learning(self, windows, step):\n")
        f.write("        pass\n\n")
        f.write("    def detection(self, window, step):\n")
        f.write("        pass\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, help="Algorithm name", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    name = args.name

    fname = "{}/algorithms/{}.py".format(root_directory, name)

    if os.path.exists(fname):
        print ("The same name of the algorithm exists. Please insert another name for the algorithm to be defined")
        sys.exit(1)

    generate_template(name)

if __name__ == "__main__":
    main()
