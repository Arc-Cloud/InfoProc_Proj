	component platform is
		port (
			clk_clk                                 : in    std_logic := 'X'; -- clk
			reset_reset_n                           : in    std_logic := 'X'; -- reset_n
			accelerometer_spi_conduit_I2C_SDAT      : inout std_logic := 'X'; -- I2C_SDAT
			accelerometer_spi_conduit_I2C_SCLK      : out   std_logic;        -- I2C_SCLK
			accelerometer_spi_conduit_G_SENSOR_CS_N : out   std_logic;        -- G_SENSOR_CS_N
			accelerometer_spi_conduit_G_SENSOR_INT  : in    std_logic := 'X'  -- G_SENSOR_INT
		);
	end component platform;

	u0 : component platform
		port map (
			clk_clk                                 => CONNECTED_TO_clk_clk,                                 --                       clk.clk
			reset_reset_n                           => CONNECTED_TO_reset_reset_n,                           --                     reset.reset_n
			accelerometer_spi_conduit_I2C_SDAT      => CONNECTED_TO_accelerometer_spi_conduit_I2C_SDAT,      -- accelerometer_spi_conduit.I2C_SDAT
			accelerometer_spi_conduit_I2C_SCLK      => CONNECTED_TO_accelerometer_spi_conduit_I2C_SCLK,      --                          .I2C_SCLK
			accelerometer_spi_conduit_G_SENSOR_CS_N => CONNECTED_TO_accelerometer_spi_conduit_G_SENSOR_CS_N, --                          .G_SENSOR_CS_N
			accelerometer_spi_conduit_G_SENSOR_INT  => CONNECTED_TO_accelerometer_spi_conduit_G_SENSOR_INT   --                          .G_SENSOR_INT
		);

