module top (
	input  		 MAX10_CLK1_50,
	
	input  [2:0] SW,
	
	inout  		 GSENSOR_SDI,
	inout 		 GSENSOR_SDO,
	output 		 GSENSOR_CS_N,
	output 		 GSENSOR_SCLK,
	
	output [9:0] LEDR,
	output [6:0] HEX0,
	output [6:0] HEX1,
	output [6:0] HEX2,
	output [6:0] HEX3
);

wire [15:0] filter_val_x;
wire [15:0] filter_val_y;
wire [15:0] filter_val_z;
wire [9:0]  ledr;
wire [6:0]  hex_0;
wire [6:0]  hex_1;
wire [6:0]  hex_2;
wire [6:0]  hex_3;
wire [15:0] filter_val_out = SW[2] ? filter_val_x :
									 (SW[1] ? filter_val_y :
												 filter_val_z);

assign LEDR = (SW != 0) ? ledr : 0;
assign HEX0 = (SW != 0) ? hex_0 : 127;
assign HEX1 = (SW != 0) ? hex_1 : 127;
assign HEX2 = (SW != 0) ? hex_2 : 127;
assign HEX3 = (SW != 0) ? hex_3 : 127;

filter filter0 (
	.clk   (MAX10_CLK1_50),
	.sdi   (GSENSOR_SDO),
	.sdo   (GSENSOR_SDI),
	.cs_n  (GSENSOR_CS_N),
	.sclk  (GSENSOR_SCLK),
	.out_x (filter_val_x),
	.out_y (filter_val_y),
	.out_z (filter_val_z),
	.t1    (ledr)
);

hex_to_7seg seg_0 (
	.in(filter_val_out[3:0]),
	.out(hex_0)
);
hex_to_7seg seg_1 (
	.in(filter_val_out[7:4]),
	.out(hex_1)
);
hex_to_7seg seg_2 (
	.in(filter_val_out[11:8]),
	.out(hex_2)
);
hex_to_7seg seg_3 (
	.in(filter_val_out[15:12]),
	.out(hex_3)
);

platform platform0 (
	.clk_clk          (MAX10_CLK1_50),
	.reset_reset_n    (1'b1),
	.filter_x_export  (filter_val_x),
	.filter_y_export  (filter_val_y),
	.filter_z_export  (filter_val_z)
);

endmodule
