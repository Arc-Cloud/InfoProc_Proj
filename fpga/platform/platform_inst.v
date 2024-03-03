	platform u0 (
		.clk_clk                                 (<connected-to-clk_clk>),                                 //                       clk.clk
		.reset_reset_n                           (<connected-to-reset_reset_n>),                           //                     reset.reset_n
		.accelerometer_spi_conduit_I2C_SDAT      (<connected-to-accelerometer_spi_conduit_I2C_SDAT>),      // accelerometer_spi_conduit.I2C_SDAT
		.accelerometer_spi_conduit_I2C_SCLK      (<connected-to-accelerometer_spi_conduit_I2C_SCLK>),      //                          .I2C_SCLK
		.accelerometer_spi_conduit_G_SENSOR_CS_N (<connected-to-accelerometer_spi_conduit_G_SENSOR_CS_N>), //                          .G_SENSOR_CS_N
		.accelerometer_spi_conduit_G_SENSOR_INT  (<connected-to-accelerometer_spi_conduit_G_SENSOR_INT>)   //                          .G_SENSOR_INT
	);

