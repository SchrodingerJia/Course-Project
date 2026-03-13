`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 09:11:55
// Design Name:
// Module Name: displayer_tb
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
module displayer_tb(
);
reg clk;
reg rst;
reg valid;
reg [7:0] data;
wire [7:0] led_en;
wire [7:0] led_cx;
displayer u_displayer(
.clk(clk),
.rst(rst),
.valid(valid),
.data(data),
.led_en(led_en),
.led_cx(led_cx)
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
data = 8'd50;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd49;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd53;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd57;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd57;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd67;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd70;
#50;
valid = 1;
#10 valid = 0;
#200;
data = 8'd68;
#50;
valid = 1;
#10 valid = 0;
#3200000;
$finish;
end
endmodule