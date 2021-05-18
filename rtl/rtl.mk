CURR_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VLOG_SRC_FILES += $(CURR_DIR)/neuron.sv \
				  $(CURR_DIR)/winner_selection.sv \
				  $(CURR_DIR)/spike_encoder.sv \
				  $(CURR_DIR)/snn.sv
