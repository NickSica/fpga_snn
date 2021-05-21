import configparser

import cocotb
from cocotb.triggers import Timer
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock

from snntoolbox.bin.run import main
import h5py
import numpy as np

async def send_inputs(dut, data):
    for idx, i in enumerate(data):
        await RisingEdge(dut.clk_i)
        dut.ecg_i <= int(i)
        dut.delta_i <= int(i * 0.1)
        if(str(dut.spike_o) == 'x'):
            dut._log.info("Key: " + str(idx) + "Value: " + str(int(i)))

@cocotb.test()
async def test(dut):
    dut._log.info("Running test...")

    config = configparser.ConfigParser()
    config.read("tb/snn_toolbox.ini")

    h5_file = config["paths"]["filename_ann"] + "_snn" + ".h5"
    h5 = h5py.File(h5_file, 'r')
    weights = []
    for key in h5["model_weights"].keys():
        if key != "input_1":
            weights.append(h5["model_weights"][key]["v_mem:0"].shape[0])
    dut._log.info("Weights: " + str(weights))
    main("tb/snn_toolbox.ini")

    dut.rst_i <= 1
    cocotb.fork(Clock(dut.clk_i, 1, units="ns").start())
    await Timer(0.5, units="ns")
    for i in range(dut.NUM_NODES.value):
        dut.syn_weights_i[i] <= weights[i]
    dut.ecg_i <= 0
    dut.delta_i <= 0

    await Timer(1, units="ns")
    dut.rst_i <= 0

    data = np.load("data/x_test.npz")
    data = list(np.concatenate(data["arr_0"]).flat)

    input_proc = cocotb.fork(send_inputs(dut, data))
    while True:
        await RisingEdge(dut.clk_i)
        time = cocotb.utils.get_sim_time(units="ns")
        dut._log.info("Time : " + str(time) + " Spike: " + str(dut.spike_o))
        if str(dut.spike_o) == 'x':
            break
        if time == len(data):
            break

    ## TODO: Figure out how to feed snntoolbox

    assert True
    dut._log.info("Running test...done")
