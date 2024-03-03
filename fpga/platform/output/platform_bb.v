
module platform (
	clk_clk,
	filter_x_export,
	reset_reset_n,
	filter_y_export,
	filter_z_export);	

	input		clk_clk;
	input	[15:0]	filter_x_export;
	input		reset_reset_n;
	input	[15:0]	filter_y_export;
	input	[15:0]	filter_z_export;
endmodule
