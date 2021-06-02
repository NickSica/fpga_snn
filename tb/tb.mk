SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES := $(VLOG_SRC_FILES)

# Top level module in hardware
TOPLEVEL = snn

# Basename of the python test file
MODULE = snn_tb

#COCOTB_LOG_LEVEL=DEBUG
#COCOTB_SCHEDULER_DEBUG=1
COMPILE_ARGS += -g2012
SIM_BUILD := $(PWD)/sim_build
export PYTHONPATH := $(PYTHONPATH):$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

include $(shell cocotb-config --makefiles)/Makefile.sim
