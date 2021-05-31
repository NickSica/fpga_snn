import configparser

import cocotb
from cocotb.triggers import FallingEdge
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock

import pickle
import h5py
import numpy as np
from sklearn import metrics

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

    h5_file = config["paths"]["filename_ann"] + "_INI.h5"
    weights = []
    with h5py.File(h5_file, 'r') as h5:
        for weight in h5["model_weights"]["0Dense_4"]["0Dense_4"]["bias:0"]:
            round_weight = round(weight)
            if round_weight > 1:
               round_weight = 1
            elif round_weight < -1:
                round_weight = -1
            weights.append(int(round_weight))

    dut._log.info("Weights: " + str(weights))
    dut._log.info("Parameters:")
    dut._log.info("NUM_NODES: " + str(dut.NUM_NODES.value))
    dut._log.info("CLK_DIV: " + str(dut.CLK_DIV.value))
    dut._log.info("DEFAULT_UTHR: " + str(dut.DEFAULT_UTHR.value))
    dut._log.info("DEFAULT_LTHR: " + str(dut.DEFAULT_LTHR.value))
    dut._log.info("THRESHOLD: " + str(dut.THRESHOLD.value))

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

    dut._log.info("Weights:")
    for i in range(dut.NUM_NODES.value):
        dut._log.info(dut.g_neurons[i].N0.synapse_r.value)

    input_proc = cocotb.fork(send_inputs(dut, data))
    spike_output = []
    while True:
        await RisingEdge(dut.clk_i)
        time = cocotb.utils.get_sim_time(units="ns")
        #dut._log.info("Time : " + str(time) + " Spike: " + str(dut.spike_o))
        spike_output.append(int(dut.spike_o.value))
        if time == len(data) or str(dut.spike_o.value) == 'x':
            break

    y_pred = np.load("data/y_test.npz")
    y_pred = list(np.concatenate(y_pred["arr_0"]).flat)

    #with open("tb/output.data", "rb") as data_file:
    #    spike_output = pickle.load(data_file)

    with open("tb/output.data", "wb") as data_file:
        pickle.dump(spike_output, data_file)

    print("Spike output length: " + str(len(spike_output)) + " y_pred length: " + str(len(y_pred)))
    spike_output = spike_output[:len(y_pred)]
    conf_mat = metrics.confusion_matrix(spike_output, y_pred)
    conf_mat = np.flip(conf_mat)
    dut._log.info("Confusion matrix: " + str(conf_mat))
    acc = (conf_mat[0][0] + conf_mat[-1][-1]) / np.sum(conf_mat)
    dut._log.info("Accuracy 1: " + str(acc))
    acc = metrics.accuracy_score(spike_output, y_pred)
    dut._log.info("Accuracy 2: " + str(acc))

    assert True
