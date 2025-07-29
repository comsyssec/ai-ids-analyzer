import os, sys, logging
import yaml, time
import subprocess
import psutil

def camel_code(name):
    words = []

    for word in name.split("_"):
        words.append(word.capitalize())

    return ''.join(words)

def is_int(value):
    ret = True
    try:
        int(value)
    except ValueError:
        ret = False
    return ret

def check_interface_availability(interface):
    ret = True
    interfaces = psutil.net_if_addrs().keys()
    logging.debug("interfaces: {}".format(interfaces))
    if interface not in interfaces:
        ret = False
    return ret

def check_file_availability(fname):
    ret = True
    if not os.path.exists(fname):
        logging.error("The file ({}) does not exist.".format(fname))
        ret = False
    return ret

def load_configuration_file(cname, root_directory):
    root_directory = os.path.abspath(root_directory)
    logging.debug("root_directory: {}".format(root_directory))
    conf = load_yaml_file(cname)

    if "general" in conf:
        conf["general"]["root_directory"] = root_directory

    for module in conf:
        for k in conf[module]:
            if "directory" in k:
                logging.debug("conf[{}][{}]: {}".format(module, k, conf[module][k]))
                conf[module][k] = os.path.join(root_directory, conf[module][k])
                logging.debug("conf[{}][{}]: {}".format(module, k, conf[module][k]))
    
    return conf

def load_yaml_file(fname):
    ret = None

    try:
        with open(fname) as f:
            ret = yaml.load(f, Loader=yaml.FullLoader)
    except:
        logging.error("The file open or the yaml syntax error happend")

    return ret

# architecture - machine - cpu
def load_qemu_availability(root_directory):
    ret = {}
    executable_arcs = [ b for b in  os.listdir("/usr/bin") + os.listdir("/bin") + os.listdir("/usr/local/bin") if "qemu-system" in b]
    executable_arcs = set(executable_arcs)
    executable_arcs.discard("qemu-system-x86_64-spice")
    for executable_arc in executable_arcs:
        arc = executable_arc.replace("qemu-system-", "")
        ret[arc] = {}

        sh_path = f'{root_directory}/scripts/qemu_availability.sh'
        arg = [arc]
        executable_machines = subprocess.run([sh_path] + arg, stdout=subprocess.PIPE, text=True)
        executable_machines = executable_machines.stdout.split("\n")[1:]
        for executable_machine in executable_machines:
            if executable_machine and executable_machine.split()[0] != "none":
                mac = executable_machine.split()[0]
                ret[arc][mac] = []

                args = [arc, mac]
                executable_cpus = subprocess.run([sh_path] + args, stdout=subprocess.PIPE, text=True)
                executable_cpus =executable_cpus.stdout.split("\n")[1:]
                
                for executable_cpu in executable_cpus:
                    if executable_cpu:
                        executable_cpu = executable_cpu.split()[0]                              
                        ret[arc][mac].append(executable_cpu)

    return ret

def process_error(request, response, ignore=False, sleep=0):
    if not response:
        logging.error("Fail to direct a physical node to execute the command")
        logging.error("    - Command: {}".format(request["command"]))
        logging.error("Please retry IoTDSCreator")
        sys.exit(1)

    if not response["returncode"] == 0 and not response["returncode"] == 2:
        if not ignore:
            logging.error("Fail to execute the command")
            logging.error("    - Returncode: {}".format(response["returncode"]))
            logging.error("Please retry IoTDSCreator")
            sys.exit(1)

    if sleep > 0:
        time.sleep(sleep)

def convert_to_seconds(dt):
    ret = 0
    dt = dt.strip()

    while len(dt) > 0:
        idx = dt.find("h")
        if idx > 0:
            ret += float(dt[0:idx]) * 3600
            dt = dt[idx+1:]
            continue

        idx = dt.find("m")
        if idx > 0:
            ret += float(dt[0:idx]) * 60
            dt = dt[idx+1:]
            continue

        idx = dt.find("s")
        if idx > 0:
            ret += float(dt[0:idx])
            dt = dt[idx+1:]
            continue

    return ret

def convert_to_megabytes(mem):
    ret = 0
    mem = mem.strip()

    while len(mem) > 0:
        idx = mem.find("T")
        if idx > 0:
            ret += float(mem[0:idx]) * 1000000
            mem = mem[idx+1:]
            continue

        idx = mem.find("G")
        if idx > 0:
            ret += float(mem[0:idx]) * 1000
            mem = mem[idx+1:]
            continue

        idx = mem.find("M")
        if idx > 0:
            ret += float(mem[0:idx])
            mem = mem[idx+1:]
            continue

        idx = mem.find("K")
        if idx > 0:
            ret += float(mem[0:idx]) * 0.001
            mem = mem[idx+1:]
            continue

    return ret

def convert_to_float(val):
    ret = 0
    val = val.strip()

    idx = val.find("e")
    v1 = int(val[0:idx])
    v2 = int(val[idx+1:])
    ret = v1 * (10 ** -v2)
    return ret
