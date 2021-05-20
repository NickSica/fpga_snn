`timescale 1ns/1ps

module snn
	#(parameter NUM_NODES = 1)
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
		syn_weights_r <= syn_weights_i;
	end

	spike_encoder
		#(.CLK_DIV(1200000),
		  .DEFAULT_UTHR(70),
		  .DEFAULT_LTHR(10))
		SE0 (.clk_i,
			   .rst_i,
			   .ecg_i,
			   .delta_i,
			   .spike_o(encoder_c));

	genvar i;
	generate
		for(i = 0; i < NUM_NODES; i = i + 1) begin : g_neurons
			neuron
				#(.THRESHOLD(12000))
				N0 (.clk_i,
					  .rst_i,
					  .syn_i(syn_weights_r[i]),
					  .axon_i(encoder_c),
					  .spike_o(nodes_c[i]));
		end
	endgenerate

	winner_selection
		#(.NUM_NODES(1))
		WS0 (.clk_i,
			   .rst_i,
			   .nodes_i(nodes_c),
			   .spike_o);

endmodule : snn
