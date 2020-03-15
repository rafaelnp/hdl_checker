

module source_with_error(
	input  [7:0] data_in,
	output [7:0] data_out
	);

	wire [7:0] connect = data_in;
	assign data_out = ~(connect)

endmodule: source_with_error
