`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 11:06:06
// Design Name:
// Module Name: UART
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
module UART(
input clk,
input rst,
input button,
input [7:0] data,
input uart_rx,
output uart_tx,
output [7:0] led_en,
output [7:0] led_cx
);
wire calculator_uart_tx;
wire send_uart_tx;
receive u_receive(
.clk(clk),
.rst(rst),
.uart_rx(uart_rx),
.uart_tx(calculator_uart_tx),
.led_en(led_en),
.led_cx(led_cx)
);
send u_send(
.clk(clk),
.rst(rst),
.button(button),
.data(data),
.uart_tx(send_uart_tx)
);
assign uart_tx = calculator_uart_tx & send_uart_tx;
endmodule