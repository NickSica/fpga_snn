import cocotb
from cocotb.triggers import Timer
from cocotb.triggers import FallingEdge
from cocotb.clock import Clock

import configparser

from snntoolbox.bin.run import main
import h5py

@cocotb.test()
async def test(dut):
    dut._log.info("Running test...")

    config = configparser.ConfigParser()
    config.read("tb/snn_toolbox.ini")

    main("tb/snn_toolbox.ini")
    h5_file = config["paths"]["filename_ann"] + "_INI" + ".h5"
    h5 = h5py.File(h5_file, 'r')

    cocotb.fork(Clock(dut.clk_i, 1, units="ns").start())
    await Timer(0.5, units="ns")
    dut._log.info(h5.keys())
    dut.rst_i <= 1
    dut.syn_weights_i <= 0 # TODO: parse h5 and deliver weights
    dut.ecg_i <= 0
    dut.delta_i <= 0
    await Timer(1, units="ns")
    dut.rst_i <= 0

    dut.spike_o # TODO: get spike value

    assert True
    dut._log.info("Running test...done")
