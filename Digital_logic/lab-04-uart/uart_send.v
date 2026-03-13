`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: NAME
// Engineer: ID
//
// Create Date: 2024/11/06 13:26:49
// Design Name:
// Module Name: uart_send
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
module uart_send(
input        clk,
input        rst,
input        valid,       // indicates data is valid （logic high (1)）, last one clock
input [7:0]  data,        // data to send
output reg   dout         // connect to usb_uart tx pin
);
localparam IDLE  = 2'b00;   // 空闲态，发送高电平
localparam START = 2'b01;   // 起始态，发送起始位
localparam DATA  = 2'b10;   // 数据态，将8位数据位发送出去
localparam STOP  = 2'b11;   // 停止态，发送停止位
reg [1:0] current_state;
reg [1:0] next_state;
reg [7:0] buffer_data;
always @(posedge clk or posedge rst) begin
if(rst) buffer_data <= 8'b0;
else if(valid) buffer_data <= data;
end
wire [31:0] index;
wire pulse;
counter #(104160,-1,8,0) u_counter(
.clk(clk),
.rst(rst),
.start_signal(valid),
.digital_signal(index),
.pulse_signal(pulse)
);
// 第1个always块，描述次态迁移到现态
always @(posedge clk or posedge rst) begin
if(rst)         current_state <= IDLE;
else if(current_state == IDLE & valid)  current_state <= next_state;
else if(pulse) current_state <= next_state;
end
// 第2个always块，描述状态转移条件判断
always @(*) begin
case (current_state)
IDLE:if(valid)     next_state = START;
else          next_state = IDLE;
START:              next_state = DATA;
DATA:if(index==7)  next_state = STOP;
else          next_state = DATA;
STOP:if(valid)     next_state = START;
else          next_state = IDLE;
default:          next_state = IDLE;
endcase
end
// 第3个always块，描述输出逻辑
always @(posedge clk or posedge rst) begin
if(rst) dout = 1'b0;
else begin
case(current_state)
IDLE:       dout = 1'b1;
START:      dout = 1'b0;
DATA:       dout = buffer_data[index];
STOP:       dout = 1'b1;
default:   dout = 1'b1;
endcase
end
end
endmodule