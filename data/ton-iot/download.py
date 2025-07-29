import kagglehub
import os
import argparse
import logging
import shutil
import random
import pandas as pd

def extract_header(fname):
    with open(fname, "r") as f:
        header = f.readline()
        tmp = header.split(",")

        attr = []
        for e in tmp:
            attr.append(e.strip().lower())

        attr[-2] = "attack_flag"
        attr[-1] = "attack_name"
        attr.append("attack_step")

        with open("header", "w") as of:
            of.write(','.join(attr))

def split_dataset():
    labels = []
    
    lines = 0
    with open("tmp", "r") as f:
        for line in f:
            lines += 1

    with open("train", "w") as of1:
        with open("test", "w") as of2:
            tmax = lines * 0.5
            num = 0
            with open("tmp", "r") as f:
                f.readline()
                for line in f:
                    tmp = line.strip().split(",")
                    label = tmp[-1].strip().lower()

                    if label not in labels:
                        labels.append(label)

                    out = "{},{}\n".format(','.join(tmp[:-1]), label)
                    rand = random.random()
                    #if num < tmax:
                    if rand < 0.7:
                        of1.write(out)
                    else:
                        of2.write(out)
                    num += 1

def label_attack_step():
    header = open("header", "r").readline()

    step = {}
    step["benign"] = "benign"
    step["dos"] = "action"
    step["injection"] = "infection"
    step["ddos"] = "action"
    step["scanning"] = "reconnaissance"
    step["password"] = "infection"
    step["mitm"] = "infection"
    step["xss"] = "infection"
    step["backdoor"] = "installation"
    step["ransomware"] = "action"

    with open("training-flow.csv", "w") as of:
        of.write("{}\n".format(header))
        with open("train", "r") as f:
            for line in f:
                tmp = line.strip().split(",")
                aname = tmp[-1]
                
                for k in step:
                    if k in aname:
                        tmp.append(step[k])
                        break

                of.write("{}\n".format(','.join(tmp)))

    with open("test-flow.csv", "w") as of:
        of.write("{}\n".format(header))
        with open("test", "r") as f:
            for line in f:
                tmp = line.strip().split(",")
                aname = tmp[-1]
                
                for k in step:
                    if k in aname:
                        tmp.append(step[k])
                        break
                
                of.write("{}\n".format(','.join(tmp)))

def finalize():
    files = ["train", "test", "header", "labels", "tmp"]
    for fname in files:
        if os.path.exists(fname):
            os.remove(fname)

def download(tdir):
    logging.info("Download the datasets")
    path = kagglehub.dataset_download("dhoogla/nftoniot", force_download=True)

    logging.info("Move ToN-IoT datasets to {}".format(path))
    for fname in os.listdir(path):
        fpath = "{}/{}".format(os.getcwd(), fname)
        if os.path.exists(fpath):
            os.remove(fpath)
        shutil.move("{}/{}".format(path, fname), os.getcwd())
    files = [f for f in os.listdir(".") if ".parquet" in f]
    
    for fname in files:
        df = pd.read_parquet(fname)
        df.to_csv("tmp", index=False)

    logging.info("Extract the header")
    extract_header("tmp")
    logging.info("Split the dataset")
    split_dataset()
    logging.info("Add the name of the attack step")
    label_attack_step()
    logging.info("Finalize preparing the dataset")
    finalize()

def main():
    download()

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", help="Target directory", type=str, default=".")
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", default="INFO", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not os.path.exists(args.target):
        logging.error("The target directory does not exist.")
        sys.exit(1)

    download(args.target)

if __name__ == "__main__":
    main()
