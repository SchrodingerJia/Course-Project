`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 08:30:07
// Design Name:
// Module Name: counter
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
module counter #(
parameter T = 100, //周期 单位为ns
parameter first_number = 0, //起始数字
parameter final_number = 7, //结束数字
parameter circulation = 0 //是否循环
)(
input clk, //时钟信号
input rst, //重置信号
input start_signal, //启动信号
output [31:0] digital_signal, //起始数字自增到结束数字信号
output pulse_signal, //周期为T的单脉冲信号
output half_pulse_signal //周期为T的单脉冲信号
);
///计数间隔
reg [31:0] cnt_max = T/10;
reg [31:0] cnt = 32'b0;
reg cnt_inc;
wire cnt_end = cnt_inc & cnt == cnt_max;
wire cnt_half = cnt_inc & cnt == cnt_max/2;
wire cnt_start = start_signal | cnt_end;
always @(posedge clk or posedge rst) begin
if(rst) cnt_inc <= 1'b0;
else if(cnt_start) cnt_inc <= 1'b1;
else if(cnt_end) cnt_inc <= 1'b0;
end
always @(posedge clk or posedge rst) begin
if(rst) cnt <= 32'b1;
else if(start_signal) cnt <= 32'b1;
else if(cnt_end) cnt <= 32'b1;
else if(cnt_inc) cnt <= cnt + 32'b1;
end
///计数
reg [31:0] count;
reg count_inc;
wire count_end = count_inc & count == final_number;
wire count_start = start_signal | (count_end & circulation);
always @(posedge clk or posedge rst) begin
if(rst) count_inc <= 1'b0;
else if(count_start) count_inc <= 1'b1;
else if(cnt_end & count_end) count_inc <= 1'b0;
end
always @(posedge clk or posedge rst) begin
if(rst) count <= first_number;
else if(start_signal) count <= first_number;
else if(cnt_end) begin
if(count_end) count <= circulation? first_number:final_number;
else if(count_inc) count <= count + 32'b1;
end
end
assign digital_signal = count;
assign pulse_signal = cnt_end;
assign half_pulse_signal = cnt_half;
endmodule