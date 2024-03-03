	component platform is
		port (
			clk_clk         : in std_logic                     := 'X';             -- clk
			filter_x_export : in std_logic_vector(15 downto 0) := (others => 'X'); -- export
			reset_reset_n   : in std_logic                     := 'X';             -- reset_n
			filter_y_export : in std_logic_vector(15 downto 0) := (others => 'X'); -- export
			filter_z_export : in std_logic_vector(15 downto 0) := (others => 'X')  -- export
		);
	end component platform;

	u0 : component platform
		port map (
			clk_clk         => CONNECTED_TO_clk_clk,         --      clk.clk
			filter_x_export => CONNECTED_TO_filter_x_export, -- filter_x.export
			reset_reset_n   => CONNECTED_TO_reset_reset_n,   --    reset.reset_n
			filter_y_export => CONNECTED_TO_filter_y_export, -- filter_y.export
			filter_z_export => CONNECTED_TO_filter_z_export  -- filter_z.export
		);

