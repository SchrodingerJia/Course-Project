`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 09:35:58
// Design Name:
// Module Name: receive
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
module receive(
input clk,
input rst,
input uart_rx,
output uart_tx,
output [7:0] led_en,
output [7:0] led_cx
);
wire valid;
wire [7:0] data;
uart_recv u_uart_recv(
.clk(clk),
.rst(rst),
.din(uart_rx),
.valid(valid),
.data(data)
);
displayer u_displayer(
.clk(clk),
.rst(rst),
.valid(valid),
.data(data),
.led_en(led_en),
.led_cx(led_cx)
);
calculator u_calculator(
.clk(clk),
.rst(rst),
.valid(valid),
.data(data),
.uart_tx(uart_tx)
);
endmodule