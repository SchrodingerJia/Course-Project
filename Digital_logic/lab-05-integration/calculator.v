`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/13 19:16:25
// Design Name:
// Module Name: calculator
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
module calculator(
input clk,
input rst,
input valid,
input [7:0] data,
output uart_tx
);
//数据读取
reg [7:0] buffer_data [2:0];
integer i;
always @(posedge clk or posedge rst) begin
if(rst) for(i=0;i<3;i=i+1) buffer_data[i] <= 8'hff;
else if(valid) begin
for(i=7;i>0;i=i-1) buffer_data[i] <= buffer_data[i-1];
buffer_data[0] <= data;
end
end
//数据转义
reg [7:0] string [2:0];
always @(posedge clk or posedge rst) begin
if(rst) for(i=0;i<3;i=i+1) string[i] <= 8'hff;
else begin
for(i=0;i<3;i=i+1) begin
case(buffer_data[i])
8'h30:      string[i] <= 8'h00;
8'h31:      string[i] <= 8'h01;
8'h32:      string[i] <= 8'h02;
8'h33:      string[i] <= 8'h03;
8'h34:      string[i] <= 8'h04;
8'h35:      string[i] <= 8'h05;
8'h36:      string[i] <= 8'h06;
8'h37:      string[i] <= 8'h07;
8'h38:      string[i] <= 8'h08;
8'h39:      string[i] <= 8'h09;
8'h41:      string[i] <= 8'h0A;
8'h42:      string[i] <= 8'h0B;
8'h43:      string[i] <= 8'h0C;
8'h44:      string[i] <= 8'h0D;
8'h45:      string[i] <= 8'h0E;
8'h46:      string[i] <= 8'h0F;
8'hff:      string[i] <= 8'hFF;
8'd43:      string[i] <= 8'h11;//+
8'd45:      string[i] <= 8'h12;//-
8'd42:      string[i] <= 8'h13;//*
8'd47:      string[i] <= 8'h14;///
default:   string[i] <= 8'hFF;
endcase
end
end
end
//计算结果
reg [7:0] result;
always @(posedge clk or posedge rst) begin
if(rst) result <= 8'hff;
else begin
case(string[1])
8'h11: result <= string[2] + string[0];
8'h12: result <= string[2] - string[0];
8'h13: result <= string[2] * string[0];
8'h14: result <= string[2] / string[0];
default: result <= result;
endcase
end
end
//转ASCII
reg [7:0] result_str;
always @(*) begin
if(rst) result_str = 8'hff;
else begin
case(result)
8'h00:      result_str = 8'h30;
8'h01:      result_str = 8'h31;
8'h02:      result_str = 8'h32;
8'h03:      result_str = 8'h33;
8'h04:      result_str = 8'h34;
8'h05:      result_str = 8'h35;
8'h06:      result_str = 8'h36;
8'h07:      result_str = 8'h37;
8'h08:      result_str = 8'h38;
8'h09:      result_str = 8'h39;
8'h0A:      result_str = 8'h41;
8'h0B:      result_str = 8'h42;
8'h0C:      result_str = 8'h43;
8'h0D:      result_str = 8'h44;
8'h0E:      result_str = 8'h45;
8'h0F:      result_str = 8'h46;
8'hFF:      result_str = 8'hff;
default:   result_str = 8'hFF;
endcase
end
end
//输出判定
wire send_valid;
wire string_valid;
assign string_valid = (string[1] >= 8'h11) & (string[1] <= 8'h14);
reg [2:0] sig;
always @(posedge clk or posedge rst) begin
if(rst) begin
sig[2] <= 1'b0;
sig[1] <= 1'b0;
sig[0] <= 1'b0;
end
else begin
sig[2] <= sig[1];
sig[1] <= sig[0];
sig[0] <= string_valid;
end
end
assign send_valid = sig[1] & ~sig[2];
//发送数据
uart_send u_uart_send(
.clk(clk),
.rst(rst),
.valid(send_valid),
.data(result_str),
.dout(uart_tx)
);
endmodule