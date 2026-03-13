`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/06 14:16:02
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
module UART #(
parameter N = 100000000
)(
input clk,
input rst,
input start,
output uart_tx
);
wire timer;
wire [31:0] index;
counter #(N,1,10,1) u_counter(
.clk(clk),
.rst(rst),
.start_signal(start),
.digital_signal(index),
.pulse_signal(timer)
);
reg [7:0] data;
always @(*) begin
case(index)
1:data = 8'd50;//2
2:data = 8'd48;//0
3:data = 8'd50;//2
4:data = 8'd51;//3
5:data = 8'd51;//3
6:data = 8'd49;//1
7:data = 8'd49;//1
8:data = 8'd65;//A
9:data = 8'd49;//1
10:data = 8'd49;//1
default:data = 8'hff;
endcase
end
wire valid;
assign valid = timer | start;
uart_send u_uart_send(
.clk(clk),
.rst(rst),
.valid(valid),
.data(data),
.dout(uart_tx)
);
endmodule