module winner_selection
	#(parameter NUM_NODES = 1)
	(input  logic clk_i,
	 input  logic rst_i,
	 input  logic [NUM_NODES - 1:0] nodes_i,
	 output logic spike_o);

	logic [31:0] node_c [0:NUM_NODES - 1];

	genvar i;
	generate
		for(i = 0; i < NUM_NODES; i = i + 1) begin : g_nodes
			always_ff @(posedge clk_i) begin : p_nodes
				if(rst_i) begin
					node_c[i] <= '0;
				end else begin
					node_c[i] <= node_c[i] + nodes_i[i];
				end
			end
		end
	endgenerate

	always_comb begin : p_spike
		logic [31:0] max_c = '0;
		logic [$clog2(NUM_NODES):0] max_node_c = '0;
		if(rst_i) begin
			max_c = '0;
			max_node_c = '0;
			spike_o = '0;
		end else begin
			for(int i = 1; i < NUM_NODES; i = i + 1) begin
				if(node_c[i] > max_c) begin
					max_c = node_c[i];
					max_node_c = i;
				end
			end
			spike_o = nodes_i[max_node_c];
		end
	end

endmodule : winner_selection
