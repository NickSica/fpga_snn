import configparser
import os
import subprocess

import h5py

def setup():
    config = configparser.ConfigParser()
    config.read("tb/snn_toolbox.ini")

    h5_file = config["paths"]["filename_ann"] + "_snn" + ".h5"
    h5 = h5py.File(h5_file, 'r')

    # Takes the first threshold and runs with it
    v_thresh = h5["model_weights"]["0Dense_2"]["v_thresh:0"].shape
    param_str = ""
    if not v_thresh:
        param_str = " -Psnn.THRESHOLD=5"
    else:
        param_str = " -Psnn.THRESHOLD=" + h5["model_weights"]["0Dense_2"]["v_thresh:0"].shape[0]

    param_str += " -Psnn.NUM_NODES=4"
    if "COMPILE_ARGS" in os.environ:
        os.environ["COMPILE_ARGS"] = os.environ["COMPILE_ARGS"] + param_str
    else:
        os.environ["COMPILE_ARGS"] = param_str

    print(os.getcwd())
    run_make = "make -f " + os.getcwd() + "/tb/tb.mk"
    make_proc = subprocess.run(run_make, shell=True, stderr=subprocess.STDOUT)
    ## Loops through all the h5 values- not needed atm
    #for key in h5["model_weights"].keys():
    #    for key, value in dict(h5["model_weights"][key]).items():
    #        if key == "v_thresh":


if __name__ == "__main__":
    setup()
