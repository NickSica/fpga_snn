module neuron
	#(parameter THRESHOLD = 100)
	(input  logic clk_i,
	 input  logic rst_i,
	 input  logic [1:0] syn_i,
	 input  logic axon_i,
	 output logic spike_o);

	localparam NUM_BITS_DENDRITE = $rtoi($ceil($clog2(THRESHOLD))) - 1;
	logic [1:0] synapse_r;
	logic [1:0] syn_out_c;
	logic signed [NUM_BITS_DENDRITE:0] dendrite_r;

	always_ff @(posedge clk_i) begin : p_load_synapse
		if(rst_i) begin
			synapse_r <= syn_i;
		end
	end

	always_comb begin : p_synapse
		if(rst_i) begin
			syn_out_c = '0;
		end else if(axon_i) begin
			syn_out_c = synapse_r;
		end else begin
			syn_out_c = '0;
		end
	end

	always_ff @(posedge clk_i) begin : p_counter
		logic [NUM_BITS_DENDRITE:0] syn_out_v = {{($bits(dendrite_r) - 1){syn_out_c[1]}}, syn_out_c[0]};
		if(rst_i) begin
			dendrite_r <= '0;
		end else if(spike_o) begin
			dendrite_r <= {$bits(dendrite_r){1'b0}} + $signed(syn_out_v);
		end else begin
			dendrite_r <= dendrite_r + $signed(syn_out_v);
		end
	end

	always_comb begin : p_comparator
		spike_o = dendrite_r >= THRESHOLD;
	end

endmodule : neuron
