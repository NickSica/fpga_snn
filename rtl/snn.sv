`timescale 1ns/1ps

module snn
	#(parameter NUM_NODES = 1,
	  parameter CLK_DIV = 1200000,
	  parameter DEFAULT_UTHR = 1,
	  parameter DEFAULT_LTHR = 0,
	  parameter THRESHOLD = 0)
	(input  logic clk_i,
	 input  logic rst_i,
	 input  logic [31:0] ecg_i,
	 input  logic [31:0] delta_i,
	 input  logic [1:0] syn_weights_i [0:NUM_NODES - 1],
	 output logic spike_o);

	logic encoder_c;
	logic [NUM_NODES - 1:0] nodes_c;
	logic [1:0] syn_weights_r [0:NUM_NODES - 1];

	always_ff @(posedge clk_i) begin : p_load_weights
		for(int i = 0; i < NUM_NODES; i++) begin
			syn_weights_r[i] <= syn_weights_i[i];
		end
	end

	spike_encoder
		#(.CLK_DIV(CLK_DIV),
		  .DEFAULT_UTHR(DEFAULT_UTHR),
		  .DEFAULT_LTHR(DEFAULT_LTHR))
		SE0 (.clk_i,
			   .rst_i,
			   .ecg_i,
			   .delta_i,
			   .spike_o(encoder_c));

	genvar i;
	generate
		for(i = 0; i < NUM_NODES; i = i + 1) begin : g_neurons
			neuron
				#(.THRESHOLD(THRESHOLD))
				N0 (.clk_i,
					  .rst_i,
					  .syn_i(syn_weights_r[i]),
					  .axon_i(encoder_c),
					  .spike_o(nodes_c[i]));
		end
	endgenerate

	winner_selection
		#(.NUM_NODES(NUM_NODES))
		WS0 (.clk_i,
			   .rst_i,
			   .nodes_i(nodes_c),
			   .spike_o);

endmodule : snn
