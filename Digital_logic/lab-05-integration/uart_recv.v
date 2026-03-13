`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/12 08:29:48
// Design Name:
// Module Name: uart_recv
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
module uart_recv(
input                   clk,
input                   rst,
input                   din,   // connect to usb_uart rx pin
output reg              valid, // indicates data is valid （logic high (1)）, last one clock
output reg [7:0]        data
);
localparam IDLE  = 2'b00;
localparam START = 2'b01;
localparam DATA  = 2'b10;
localparam STOP  = 2'b11;
reg [1:0] current_state;
reg [1:0] next_state;
reg [7:0] buffer_data;
always @(posedge clk or posedge rst) begin
if(rst) buffer_data <= 8'b0;
else if(half_pulse & current_state == DATA) buffer_data[index] <= din;
end
wire start;
reg s_sig_0;
reg s_sig_1;
always @(posedge clk or posedge rst) begin
if(rst) begin
s_sig_1 <= 1'b1;
s_sig_0 <= 1'b1;
end
else if(current_state == IDLE | current_state == STOP) begin
s_sig_1 <= s_sig_0;
s_sig_0 <= din;
end
else begin
s_sig_1 <= 1'b1;
s_sig_0 <= 1'b1;
end
end
assign start = ~s_sig_0 & s_sig_1;
wire [31:0] index;
wire pulse,half_pulse;
counter #(104160,-1,8,0) u_counter(
.clk(clk),
.rst(rst),
.start_signal(start),
.digital_signal(index),
.pulse_signal(pulse),
.half_pulse_signal(half_pulse)
);
// 第1个always块，描述次态迁移到现态
always @(posedge clk or posedge rst) begin
if(rst)         current_state <= IDLE;
else if(current_state == IDLE & ~din)  current_state <= next_state;
else if(pulse) current_state <= next_state;
end
// 第2个always块，描述状态转移条件判断
always @(*) begin
case (current_state)
IDLE:if(din)       next_state = IDLE;
else          next_state = START;
START:             next_state = DATA;
DATA:if(index==7)  next_state = STOP;
else          next_state = DATA;
STOP:if(din)       next_state = IDLE;
else          next_state = START;
default:           next_state = IDLE;
endcase
end
// 第3个always块，描述输出逻辑
always @(posedge clk or posedge rst) begin
if(rst) valid = 1'b0;
else if(current_state == STOP) valid = half_pulse;
end
always @(posedge clk or posedge rst) begin
if(rst) data = 8'b0;
else begin
case(current_state)
IDLE:           data = data;
START:          data = data;
DATA:           data = data;
STOP:           data = buffer_data;
default:        data = data;
endcase
end
end
endmodule