module spike_encoder
	#(parameter CLK_DIV = 1200000)
	(input logic  clk_i,
	 input logic  rst_i,
	 input logic [31:0] ecg_i,
	 input logic [31:0] delta_i,
	 output logic spike_o);

	logic clk_r;
	logic [31:0] cnt_r;
	logic [31:0] uthr_r;
	logic [31:0] lthr_r;
	logic [31:0] uthr_c;
	logic [31:0] lthr_c;
	logic [31:0] add_c;
	logic [31:0] sub_c;
	logic dff_en_c;
	logic comp2_en_c;
	logic first_stage_comp_c;
	logic second_stage_comp_c;

	assign dff_en_c = first_stage_comp_c | second_stage_comp_c;
	assign comp2_en_c = (~first_stage_comp_c) & clk_r;

	always_ff @(posedge clk_i) begin : p_clk_div
		if(rst_i) begin
			cnt_r <= '0;
			clk_r <= 1'b0;
		end else if(cnt_r = CLK_DIV - 1) begin
			cnt_r <= '0;
			clk_r <= ~clk_r;
		end else begin
			cnt_r <= cnt_r + 1'b1;
			clk_r <= clk_r;
		end
	end

	always_ff @(posedge clk_i) begin : p_dff
		if(dff_en_c) begin
			uthr_r <= uthr_c;
			lthr_r <= lthr_c;
		end else begin
			uthr_r <= uthr_r;
			lthr_r <= lthr_r;
		end
	end

	always_comb begin : p_uthr_mux
		if(first_stage_comp_c == 1'b1) begin
			uthr_c = adder_c;
		end else if(second_stage_comp_c == 1'b1) begin
			uthr_c = lthr_r;
		end else begin
			uthr_c = '0;
		end
	end

	always_comb begin : p_lthr_mux
		if(first_stage_comp_c == 1'b1) begin
			lthr_c = uthr_r;
		end else if(second_stage_comp_c == 1'b1) begin
			lthr_c = sub_c;
		end else begin
			lthr_c = '0;
		end
	end

	always_comb begin : p_comp1
		if(clk_r) begin
			first_stage_comp_c = ecg_i == add_c;
		end else begin
			first_stage_comp_c = 1'b0;
		end
	end

	always_comb begin : p_comp2
		if(comp2_en_c) begin
			second_stage_comp_c = ecg_i == sub_c;
		end else begin
			second_stage_comp_c = 1'b0;
		end
	end

	always_comb begin : p_add
		if(clk_r) begin
			add_c = uthr_r + delta_i;
		end else begin
			add_c = '0;
		end
	end

	always_comb begin : p_sub
		if(second_stage_comp_c) begin
			sub_c = lthr_r - delta_i;
		end else begin
			sub_c = '0;
		end
	end

	assign spike_o = first_stage_comp_c;
endmodule spike_encoder
