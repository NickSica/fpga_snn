import cocotb
from cocotb.triggers import Timer
from cocotb.triggers import FallingEdge
from cocotb.clock import Clock

@cocotb.test()
async def test(dut):
    dut._log.info("Running test...")
    cocotb.fork(Clock(dut.clk, 1, units="ns").start())
