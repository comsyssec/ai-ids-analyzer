import kagglehub
import os
import argparse
import logging
import shutil
import random

def extract_header(fname):
    with open(fname, "r") as f:
        header = f.readline()
        tmp = header.split(",")
        
        attr = []
        for e in tmp:
            attr.append(e.strip().lower())

        attr[-1] = "attack_name"
        attr.append("attack_flag")
        attr.append("attack_step")

        with open("header", "w") as of:
            of.write(','.join(attr))

def combine_all(files):
    labels = []

    lines = {}
    for fname in files:
        lines[fname] = 0
        with open(fname, "r") as f:
            for line in f:
                lines[fname] += 1

    with open("train", "w") as of1:
        with open("test", "w") as of2:
            for fname in files:
                logging.info(" - Add the file: {}".format(fname))
                tmax = lines[fname] * 0.5
                num = 0
                with open(fname, "r") as f:
                    f.readline()
                    for line in f:
                        if "NaN" in line or "Infinity" in line:
                            continue
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

    with open("labels", "w") as of:
        of.write(','.join(labels))

def label_attack_step():
    header = open("header", "r").readline()

    step = {}
    step["benign"] = "benign"
    step["ddos"] = "action"
    step["brute force"] = "infection"
    step["xss"] = "infection"
    step["sql injection"] = "infection"
    step["ftp-patator"] = "infection"
    step["ssh-patator"] = "infection"
    step["infiltration"] = "action"
    step["bot"] = "installation"
    step["portscan"] = "reconnaissance"
    step["dos slowloris"] = "action"
    step["dos slowhttptest"] = "action"
    step["dos hulk"] = "action"
    step["dos goldeneye"] = "action"
    step["heartbleed"] = "infection"

    with open("training-flow.csv", "w") as of:
        of.write("{}\n".format(header))
        with open("train", "r") as f:
            for line in f:
                tmp = line.strip().split(",")
                aname = tmp[-1]
                if "benign" not in aname:
                    tmp.append("1")
                else:
                    tmp.append("0")

                for k in step:
                    if k in aname:
                        tmp[-2] = k
                        tmp.append(step[k])
                        break
                of.write("{}\n".format(','.join(tmp)))

    with open("test-flow.csv", "w") as of:
        of.write("{}\n".format(header))
        with open("test", "r") as f:
            for line in f:
                tmp = line.strip().split(",")
                aname = tmp[-1]
                if "benign" not in aname:
                    tmp.append("1")
                else:
                    tmp.append("0")

                for k in step:
                    if k in aname:
                        tmp.append(step[k])
                        break
                of.write("{}\n".format(','.join(tmp)))

def finalize():
    if os.path.exists("train"):
        os.remove("train")

    if os.path.exists("test"):
        os.remove("test")

    if os.path.exists("header"):
        os.remove("header")

    if os.path.exists("labels"):
        os.remove("labels")

def download(tdir):
    logging.info("Download the datasets")
    path = kagglehub.dataset_download("chethuhn/network-intrusion-dataset", force_download=True)

    logging.info("Move CIC-IDS-2017 datasets to {}".format(path))
    for fname in os.listdir(path):
        fpath = "{}/{}".format(os.getcwd(), fname)
        if os.path.exists(fpath):
            os.remove(fpath)
        shutil.move("{}/{}".format(path, fname), os.getcwd())

    files = [f for f in os.listdir(".") if ".csv" in f]
    if "training-flow.csv" in files:
        files.remove("training-flow.csv")
    if "test-flow.csv" in files:
        files.remove("test-flow.csv")

    logging.info("Extract the header")
    extract_header(files[0])
    logging.info("Combine all the files into one file")
    combine_all(files)
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
