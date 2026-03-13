`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/13 20:00:04
// Design Name:
// Module Name: calculator_tb
// Project Name:
// Target Devices:
// Tool Versions:
// Description:
//
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////
module calculator_tb(
);
reg clk;
reg rst;
reg valid;
reg [7:0] data;
wire uart_tx;
calculator u_calculator(
.clk(clk),
.rst(rst),
.valid(valid),
.data(data),
.uart_tx(uart_tx)
);
always #5 clk = ~clk;
initial begin
clk = 0;
rst = 1'b1;
valid = 0;
data = 8'b0;
#10;
rst = 0;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd48;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd49;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd50;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd51;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd43;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd50;
#50;
valid = 1;
#10 valid = 0;
#1046100;
data = 8'd57;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd47;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd51;
#50;
valid = 1;
#10 valid = 0;
#1046100;
$finish;
end
endmodule