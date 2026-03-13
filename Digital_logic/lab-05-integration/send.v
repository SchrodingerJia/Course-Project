`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 11:04:36
// Design Name:
// Module Name: send
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
module send(
input clk,
input rst,
input button,
input [7:0] data,
output uart_tx
);
//按键检测
///第一上升沿检测
integer j;
wire pos_edge_1;
reg [2:0] sig_1 [2:0];
always @ (posedge clk or posedge rst) begin
if(rst) for (j=0;j<3;j=j+1) sig_1[j] <= 1'b0;
else begin
sig_1[2] <= sig_1[1];
sig_1[1] <= sig_1[0];
sig_1[0] <= button;
end
end
assign pos_edge_1 = ~sig_1[2] & sig_1[1];
///上升沿后开始计数10ms
wire button_valid;
counter #(10000000,0,1,0) u_counter(
.clk(clk),
.rst(rst),
.start_signal(pos_edge_1),
.digital_signal(button_valid),
.pulse_signal(),
.half_pulse_signal()
);
///第二上升沿检测
integer l;
wire pos_edge_2;
reg [2:0] sig_2 [2:0];
always @ (posedge clk or posedge rst) begin
if(rst) for (l=0;l<3;l=l+1) sig_2[l] <= 1'b0;
else begin
sig_2[2] <= sig_2[1];
sig_2[1] <= sig_2[0];
sig_2[0] <= button_valid;
end
end
assign pos_edge_2 = ~sig_2[2] & sig_2[1] & button;
//发送数据
uart_send u_uart_send(
.clk(clk),
.rst(rst),
.valid(pos_edge_2),
.data(data),
.dout(uart_tx)
);
endmodule