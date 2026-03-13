`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/10/22 08:35:48
// Design Name:
// Module Name: flowing_water_lights
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
module flowing_water_lights#(
parameter N = 27'd1000000
)
(
input clk,
input rst,
input button,
input [1:0] freq_set,
input dir_set,
output reg [7:0] led
);
//频率选择
reg [26:0] CNT_MAX;
always @ (*) begin
case(freq_set)
2'b00:CNT_MAX <= N-2;
2'b01:CNT_MAX <= 10*N-2;
2'b10:CNT_MAX <= 25*N-2;
2'b11:CNT_MAX <= 50*N-2;
default:;
endcase
end
//启停控制：按下button反转en状态，en=1时启动
integer i;
wire pos_edge;
reg [2:0] sig [2:0];
reg en;
always @ (posedge clk or posedge rst) begin
if(rst) for (i=0;i<3;i=i+1) sig[i] <= 1'b0;
else begin
sig[2] <= sig[1];
sig[1] <= sig[0];
sig[0] <= button;
end
end
assign pos_edge = ~sig[2] & sig[1] ;
always @ (posedge clk or posedge rst) begin
if(rst) en <= 1'b0;
else if(pos_edge) en <= ~en;
end
//计数器：产生频率为100Mhz/CNT_MAX的cnt_end信号
reg [26:0] count;
reg cnt_inc;
wire cnt_end = cnt_inc & count == CNT_MAX;
always @ (posedge clk or posedge rst) begin
if(rst) cnt_inc <= 1'b0;
else if(en) begin
if(cnt_end) cnt_inc <= 1'b0;
else cnt_inc <= 1'b1;
end
else cnt_inc <= cnt_inc;
end
always @ (posedge clk or posedge rst) begin
if(rst) count <= 27'b0;
else if(en) begin
if(cnt_end) count <= 27'b0;
else if(cnt_inc) count <= count + 27'b1;
end
end
//流水灯
always @ (posedge clk or posedge rst) begin
if(rst) led <= 8'b00000001;
else if(cnt_end) begin
if(dir_set) led <= {led[0], led[7:1]};
else led <= {led[6:0], led[7]};
end
end
endmodule