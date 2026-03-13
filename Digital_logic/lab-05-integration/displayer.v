`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 08:32:35
// Design Name:
// Module Name: displayer
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
module displayer(
input clk,
input rst,
input valid,
input [7:0] data,
output reg [7:0] led_en,
output reg [7:0] led_cx
);
//数据读取
reg [7:0] buffer_data [7:0];
integer i;
always @(posedge clk or posedge rst) begin
if(rst) for(i=0;i<8;i=i+1) buffer_data[i] <= 8'hff;
else if(valid) begin
for(i=7;i>0;i=i-1) buffer_data[i] <= buffer_data[i-1];
buffer_data[0] <= data;
end
end
//数据转义
reg [7:0] display [7:0];
always @(posedge clk or posedge rst) begin
if(rst) for(i=0;i<8;i=i+1) display[i] <= 8'hff;
else begin
for(i=0;i<8;i=i+1) begin
case(buffer_data[i])
8'h30:      display[i] <= 8'h00;
8'h31:      display[i] <= 8'h01;
8'h32:      display[i] <= 8'h02;
8'h33:      display[i] <= 8'h03;
8'h34:      display[i] <= 8'h04;
8'h35:      display[i] <= 8'h05;
8'h36:      display[i] <= 8'h06;
8'h37:      display[i] <= 8'h07;
8'h38:      display[i] <= 8'h08;
8'h39:      display[i] <= 8'h09;
8'h41:      display[i] <= 8'h0A;
8'h42:      display[i] <= 8'h0B;
8'h43:      display[i] <= 8'h0C;
8'h44:      display[i] <= 8'h0D;
8'h45:      display[i] <= 8'h0E;
8'h46:      display[i] <= 8'h0F;
8'hff:      display[i] <= 8'hFF;
8'd43:      display[i] <= 8'h11;//+
8'd45:      display[i] <= 8'h12;//-
8'd42:      display[i] <= 8'h13;//*
8'd47:      display[i] <= 8'h14;///
default:   display[i] <= 8'hFF;
endcase
end
end
end
//脉冲信号
wire [7:0] index;
wire pulse;
reg start;
always @(posedge clk) begin
start <= rst;
end
counter #(2000000,0,7,1) u_counter(
.clk(clk),
.rst(rst),
.start_signal(start),
.digital_signal(index),
.pulse_signal(pulse),
.half_pulse_signal()
);
//数码管编码
reg [7:0] EN_LIST [7:0];
reg [7:0] CX_LIST [32:0];
reg [7:0] DEFAULT;
always @(posedge clk or posedge rst) begin
if(rst) begin
EN_LIST[0] <= 8'h7F;
EN_LIST[1] <= 8'hBF;
EN_LIST[2] <= 8'hDF;
EN_LIST[3] <= 8'hEF;
EN_LIST[4] <= 8'hF7;
EN_LIST[5] <= 8'hFB;
EN_LIST[6] <= 8'hFD;
EN_LIST[7] <= 8'hFE;
CX_LIST[0] <= 8'h03;
CX_LIST[1] <= 8'h9F;
CX_LIST[2] <= 8'h25;
CX_LIST[3] <= 8'h0D;
CX_LIST[4] <= 8'h99;
CX_LIST[5] <= 8'h49;
CX_LIST[6] <= 8'h41;
CX_LIST[7] <= 8'h1F;
CX_LIST[8] <= 8'h01;
CX_LIST[9] <= 8'h19;
CX_LIST[10]<= 8'h11;
CX_LIST[11]<= 8'hC1;
CX_LIST[12]<= 8'hE5;
CX_LIST[13]<= 8'h85;
CX_LIST[14]<= 8'h61;
CX_LIST[15]<= 8'h71;
CX_LIST[17]<= 8'h9C;
CX_LIST[18]<= 8'hFC;
CX_LIST[19]<= 8'h90;
CX_LIST[20]<= 8'h6C;
DEFAULT <= 8'hFF;
end
end
//数码管显示
always @(posedge clk or posedge rst) begin
if(rst) begin
led_en <= EN_LIST[0];
led_cx <= DEFAULT;
end
else if(pulse) begin
led_en <= EN_LIST[index];
if(display[index] == DEFAULT) led_cx <= DEFAULT;
else led_cx <= CX_LIST[display[index]];
end
end
endmodule