vivado = vivado -mode batch -source
script = fpga_build_scripts/compile.tcl
# Can't use the V707 constraints and partNum until license server stuff is figured out
constr = boards/arty-a7-100/constraints.xdc
partNum = xc7a100tcsg324-1 #xc7vx485tffg1761-2
top = snn
outDir = build
lang = verilog
srcDir = rtl

# Currently the following is useless as the compile script just globs all it can find
VLOG_SRC_FILES :=
include rtl/rtl.mk
include tb/tb.mk

.PHONY: all

build:
	$(vivado) $(script) -tclargs -partNum $(partNum) \
								 -outDir $(outDir) \
								 -top $(top) \
								 -constrFile $(constr) \
								 -lang $(lang) \
								 -srcDir $(srcDir)

# Include cocotb's make rules to help with sim setup
cocotb:
	$(MAKE) -f tb/tb.mk

test:
	vlog -sv $(VLOG_SRC_FILES)
	vsim -do wave.do -do "run -all" +nowarn3691 tb

clean::
	-rm -r $(outDir)
	-rm -r sim_build
	-rm results.xml
	-rm -r tb/__pycache__
	-rm vivado*
	-rm webtalk*
	-rm x*
	-rm -r logs
