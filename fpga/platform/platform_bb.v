
module platform (
	clk_clk,
	reset_reset_n,
	accelerometer_spi_conduit_I2C_SDAT,
	accelerometer_spi_conduit_I2C_SCLK,
	accelerometer_spi_conduit_G_SENSOR_CS_N,
	accelerometer_spi_conduit_G_SENSOR_INT);	

	input		clk_clk;
	input		reset_reset_n;
	inout		accelerometer_spi_conduit_I2C_SDAT;
	output		accelerometer_spi_conduit_I2C_SCLK;
	output		accelerometer_spi_conduit_G_SENSOR_CS_N;
	input		accelerometer_spi_conduit_G_SENSOR_INT;
endmodule
