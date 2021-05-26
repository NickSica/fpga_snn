import configparser

import cocotb
from cocotb.triggers import Timer
from cocotb.triggers import FallingEdge
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock

from snntoolbox.bin.run import main
import pickle
import h5py
import numpy as np

async def send_inputs(dut, data):
    for idx, i in enumerate(data):
        await RisingEdge(dut.clk_i)
        dut.ecg_i <= int(i)
        dut.delta_i <= int(i * 0.1)
        if(str(dut.spike_o.value) == 'x'):
            dut._log.info("Data Length: " + str(len(data)) + " Key: " + str(idx) + " Value: " + str(int(i)))
            dut._log.info("Nodes: " + str(dut.nodes_c.value))
            dut._log.info("Dendrite: " + str(dut.g_neurons[0].N0.dendrite_r.value))
            dut._log.info("synapse_r: " + str(dut.g_neurons[0].N0.synapse_r.value) + " syn_out_c: " + str(dut.g_neurons[0].N0.syn_out_c.value))

@cocotb.test()
async def test(dut):
    dut._log.info("Running test...")

    config = configparser.ConfigParser()
    config.read("tb/snn_toolbox.ini")

    h5_file = config["paths"]["filename_ann"] + ".h5"
    h5 = h5py.File(h5_file, 'r')
    print(dict(h5["model_weights"]["dense"]["dense"]))
    print(dict(h5["model_weights"]["dense_1"]["dense_1"]))
    print(dict(h5["model_weights"]["lstm"]["lstm"]["lstm_cell"]))
    print(dict(h5["optimizer_weights"]["RMSprop"]))
    return
    weights = []
    for key in h5["model_weights"].keys():
        if key != "input_1":
            weights.append(h5["model_weights"][key]["v_mem:0"].shape[0])
    dut._log.info("Weights: " + str(weights))
    main("tb/snn_toolbox.ini")

    dut.rst_i <= 1
    cocotb.fork(Clock(dut.clk_i, 1, units="ns").start())
    await FallingEdge(dut.clk_i)

    for i in range(dut.NUM_NODES.value):
        dut.syn_weights_i[i] <= weights[i]
    dut.ecg_i <= 0
    dut.delta_i <= 0

    await FallingEdge(dut.clk_i)
    await FallingEdge(dut.clk_i)
    dut.rst_i <= 0

    data = np.load("data/x_test.npz")
    data = list(np.concatenate(data["arr_0"]).flat)

    input_proc = cocotb.fork(send_inputs(dut, data))
    spike_output = []
    while True:
        await RisingEdge(dut.clk_i)
        time = cocotb.utils.get_sim_time(units="ns")
        #dut._log.info("Time : " + str(time) + " Spike: " + str(dut.spike_o))
        spike_output.append(str(dut.spike_o.value))
        if time == len(data) or str(dut.spike_o.value) == 'x':
            break

    print(spike_output)
    with open("tb/output.data", "wb") as data_file:
        pickle.dump(spike_output, data_file)

    ## TODO: Figure out how to feed snntoolbox

    assert True
    dut._log.info("Running test...done")
