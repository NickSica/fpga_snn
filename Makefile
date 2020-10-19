vivado = vivado -mode batch -source
script = compile.tcl
tb_script = waveform.tcl
constr = ./V707/constraints.xdc

VLOG_SRC_FILES = 

.PHONY: build clean

build:
	$(vivado) $(script) -tclargs $(constr)

test:
	vlog -sv $(VLOG_SRC_FILES)
	vsim -do wave.do -do "run -all" +nowarn3691 tb

clean:
	-rm -r build
	-rm vivado*
	-rm webtalk*
	-rm x*

