module neuron
	#(parameter int THRESHOLD)
	(input  logic clk_i,
	 input  logic rst_i,
	 input  logic axon_i,
	 output logic spike_o);

	logic synapse_r;
	logic syn_out_c;
	logic dendrite_r;

	always_comb begin : p_synapse
		if(axon_i) begin
			syn_out_c = synapse_r;
		else end begin
			syn_out_c = 1'b0;
		end
	end

	always_ff @(posedge clk_i) begin : p_counter
		if(spike_o) begin
			dendrite_r <= 1'b0 + syn_out_r;
		end else begin
			dendrite_r <= dendrite_r + syn_out_r;
		end
	end

	always_comb begin : p_comparator
		spike_o = dendrite_r >= THRESHOLD;
	end

endmodule neuron
