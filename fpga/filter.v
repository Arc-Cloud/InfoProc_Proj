module filter (
	input clk,
	input sdi,
	output sdo,
	output cs_n,
	output sclk,
	output [15:0] out_x,
	output [15:0] out_y,
	output [15:0] out_z,
	output [9:0] t1
);

parameter FILTER_SHIFT = 2; 								     // Creates 2**FILTER_SHIFT registers
parameter TARG_SCLK = 2_000_000;						        // Target frequency for SCLK
parameter CLK_NUM_FOR_SCLK = 50_000_000 / TARG_SCLK;    // Base clock is 50MHz
parameter SCLK_CYCLES_BETWEEN_READS = TARG_SCLK / 3200; // Number of SCLK cycles before read is performed

reg status;
localparam IDLE = 0;
localparam SENDING = 1;
initial status = IDLE;

reg [$clog2(CLK_NUM_FOR_SCLK)/*-1*/:0]  sclk_timer;
reg sclk_reg;
always @(posedge clk)
	if (sclk_timer < CLK_NUM_FOR_SCLK)
		sclk_timer <= sclk_timer + 1;
	else
	begin
		sclk_timer <= 0;
		sclk_reg <= !sclk_reg;
	end	
assign sclk = sclk_reg || cs_n;

reg cs_n_reg;
assign cs_n = cs_n_reg;
initial cs_n_reg = 1;

reg [(($clog2(SCLK_CYCLES_BETWEEN_READS) > 4)	 // Need at least 16 states
		? $clog2(SCLK_CYCLES_BETWEEN_READS)
		: 5)/*-1*/ : 0] sclk_count;

reg [15:0] write_val;
reg [2:0] initial_instr;
localparam INITIAL_INSTR_COUNT = 2;
initial initial_instr = 0;
initial write_val = 16'b00_110001_00000000;
always @(*)
	case (initial_instr)
	0:	write_val <= 16'b00_110001_00000000; // Standard 4 lane SPI operation
	1: write_val <= 16'b00_101100_00001111; // 3200 Hz mode
	//2: write_val <= 16'b
	2: write_val <= 16'b11_110010_00000000; // Read
	endcase

	
localparam BUFFER_SIZE = (16 + 16 + 16) * (2**FILTER_SHIFT);
reg [BUFFER_SIZE-1:0] buffer;

reg sdo_reg;
assign sdo = sdo_reg;

always @(negedge sclk_reg)
begin
	if (status == IDLE)
		if (sclk_count < SCLK_CYCLES_BETWEEN_READS)
			sclk_count <= sclk_count + 1;
		else
		begin
			sclk_count <= 0;
			status <= SENDING;
		end
	else
		if (sclk_count < (initial_instr < INITIAL_INSTR_COUNT ? 16 : 8 + 16 + 16 + 16))
		begin
			cs_n_reg <= 0;
			if ((initial_instr < INITIAL_INSTR_COUNT) || (sclk_count < 8)) sdo_reg <= write_val[15-sclk_count];
			sclk_count <= sclk_count + 1;
		end
		else
		begin
			sclk_count <= 0;
			cs_n_reg <= 1;
			status <= IDLE;
			if (initial_instr < INITIAL_INSTR_COUNT) initial_instr <= initial_instr + 1;
		end
end

wire [15:0] val_x_0 = {buffer[(0*48)+39:(0*48)+32], buffer[(0*48)+47:(0*48)+40]};
wire [15:0] val_y_0 = {buffer[(0*48)+23:(0*48)+16], buffer[(0*48)+31:(0*48)+24]};
wire [15:0] val_z_0 = {buffer[(0*48)+ 7:(0*48)+ 0], buffer[(0*48)+15:(0*48)+ 8]};
wire [15:0] val_x_1 = {buffer[(1*48)+39:(1*48)+32], buffer[(1*48)+47:(1*48)+40]};
wire [15:0] val_y_1 = {buffer[(1*48)+23:(1*48)+16], buffer[(1*48)+31:(1*48)+24]};
wire [15:0] val_z_1 = {buffer[(1*48)+ 7:(1*48)+ 0], buffer[(1*48)+15:(1*48)+ 8]};
wire [15:0] val_x_2 = {buffer[(2*48)+39:(2*48)+32], buffer[(2*48)+47:(2*48)+40]};
wire [15:0] val_y_2 = {buffer[(2*48)+23:(2*48)+16], buffer[(2*48)+31:(2*48)+24]};
wire [15:0] val_z_2 = {buffer[(2*48)+ 7:(2*48)+ 0], buffer[(2*48)+15:(2*48)+ 8]};
wire [15:0] val_x_3 = {buffer[(3*48)+39:(3*48)+32], buffer[(3*48)+47:(3*48)+40]};
wire [15:0] val_y_3 = {buffer[(3*48)+23:(3*48)+16], buffer[(3*48)+31:(3*48)+24]};
wire [15:0] val_z_3 = {buffer[(3*48)+ 7:(3*48)+ 0], buffer[(3*48)+15:(3*48)+ 8]};

wire [15+FILTER_SHIFT:0] val_x_sum = val_x_0 + val_x_1 + val_x_2 + val_x_3;
wire [15+FILTER_SHIFT:0] val_y_sum = val_y_0 + val_y_1 + val_y_2 + val_y_3;
wire [15+FILTER_SHIFT:0] val_z_sum = val_z_0 + val_z_1 + val_z_2 + val_z_3;

reg [15:0] out_x_reg;
reg [15:0] out_y_reg;
reg [15:0] out_z_reg;


assign out_x = out_x_reg;
assign out_y = out_y_reg;
assign out_z = out_z_reg;

always @(posedge cs_n)
begin
	out_x_reg <= val_x_sum >> FILTER_SHIFT;
	out_y_reg <= val_y_sum >> FILTER_SHIFT;
	out_z_reg <= val_z_sum >> FILTER_SHIFT;
	s_count_reg <= s_count;
end

reg p0;
reg p1;
assign t1 = {cs_n, sclk, sdi, sdo, sdi == 0, sdo == 0, s_count_reg == 48, 1'b0, p0 && sclk_reg && !cs_n, p1 && sclk_reg && !cs_n};

reg [6:0] s_count;
reg [6:0] s_count_reg;

always @(posedge sclk_reg)
begin
	if ((status == SENDING) && (initial_instr >= INITIAL_INSTR_COUNT) && (sclk_count > 8))
	begin
		buffer <= {buffer[BUFFER_SIZE - 2:0], sdi};
		s_count <= s_count + 1;
	end
	else
		s_count <= 0;
	
	if (sdo)
	begin
		p1 <= 1;
		p0 <= 0;
	end
	else 
	begin
		p0 <= 1;
		p1 <= 0;
	end
end

endmodule
