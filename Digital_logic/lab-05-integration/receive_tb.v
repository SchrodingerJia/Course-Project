`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 10:11:33
// Design Name:
// Module Name: receive_tb
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
module receive_tb(
);
reg clk;
reg rst;
reg uart_rx;
wire uart_tx;
wire [7:0] led_en;
wire [7:0] led_cx;
receive u_receive(
.clk(clk),
.rst(rst),
.uart_rx(uart_rx),
.uart_tx(uart_tx),
.led_en(led_en),
.led_cx(led_cx)
);
always #5 clk = ~clk;
initial begin
clk = 0;
rst = 1'b1;
uart_rx = 1;
#10;
rst = 0;
#50;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#104160;
uart_rx = 1;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#1000000;
uart_rx = 0;
#104160;
uart_rx = 1;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#104160;
uart_rx = 1;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#1441600;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#104160;
uart_rx = 1;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#2345600;
uart_rx = 0;
#104160;
uart_rx = 1;
#104160;
uart_rx = 1;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#104160;
uart_rx = 1;
#104160;
uart_rx = 0;
#104160;
uart_rx = 0;
#104160;
uart_rx = 1;
#1041600;
$finish;
end
endmodule