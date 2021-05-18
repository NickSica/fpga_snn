SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES := $(VLOG_SRC_FILES)

# Top level module in hardware
TOPLEVEL = snn

# Basename of the python test file
MODULE = snn_tb

include $(shell cocotb-config --makefiles)/Makefile.sim
