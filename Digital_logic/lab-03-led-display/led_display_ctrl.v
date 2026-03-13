`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2024/10/24 16:52:15
// Design Name: 
// Module Name: led_display_ctrl
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


module led_display_ctrl#(
    parameter N = 200000
)
(
    input clk,
    input rst,
    input button,
    input cal_rst,
    input [0:7] count,
    output reg [0:7] led_en,
    output reg [0:7] led_cx
    );

//产生频率为500hz的f1信号
reg [19:0] cnt = 20'b0;
reg cnt_inc;
wire f1 = cnt_inc & cnt == N-2;
always @(posedge clk or posedge rst) begin
    if(rst) cnt_inc <= 1'b0;
    else if(f1) cnt_inc <= 1'b0;          
    else cnt_inc <= 1'b1;     
end

always @(posedge clk or posedge rst) begin
    if(rst) cnt <= 27'b0;        
    else if(f1) cnt <= 27'b0;       
    else if(cnt_inc) cnt <= cnt + 27'b1;
end

//产生0-7循环的en信号
reg [2:0] en;
always @(posedge clk or posedge rst) begin
    if(rst) en = 3'b0;
    else if(f1) en <= en + 3'b1;    
end

//数码管显示
reg [7:0] EN_LIST [7:0];
reg [7:0] CX_LIST [15:0];
reg [3:0] display [7:0];
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
        CX_LIST[15]<= 8'H71;
        
        led_en <= EN_LIST[0];
        led_cx <= CX_LIST[0];
    end
    else begin
    led_en <= EN_LIST[en];
    led_cx <= CX_LIST[display[en]];
    end
end

//学号后两位
always @(posedge clk or posedge rst) begin  
    if(rst) begin
        display[7] <= 4'h1;
        display[6] <= 4'h1;
    end
    else begin
        display[7] <= 4'h1;
        display[6] <= 4'h1;
    end
end

//拨码开关
integer i;
always @(posedge clk or posedge rst) begin
    if(rst) begin
        display[5] <= 4'h0;
        display[4] <= 4'h0;
    end
    else begin
        display[5] <= 4'h0;
        display[4] = 4'h0;
        for(i=0;i<8;i=i+1) display[4] = display[4] + count[i];
    end
end

//按键计数
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
reg [2:0] button_cnt;
reg [2:0] button_cnt_max = 3'd5;
reg button_cnt_inc;
wire button_cnt_end = button_cnt_inc & button_cnt == button_cnt_max;
always @(posedge clk or posedge rst) begin
    if(rst) button_cnt_inc <= 1'b0;
    else if(~button) button_cnt_inc <= 1'b0;
    else if(pos_edge_1) button_cnt_inc <= 1'b0;
    else if(button_cnt_end) button_cnt_inc <= 1'b0;          
    else button_cnt_inc <= 1'b1;     
end
always @(posedge clk or posedge rst) begin
    if(rst) button_cnt <= 3'b1;
    else if(~button) button_cnt <= 1'b0;
    else if(pos_edge_1) button_cnt <= 1'b0;
    else if(f1) begin
        if(button_cnt_end) button_cnt <= 3'd5;
        else if(button_cnt_inc) button_cnt <= button_cnt + 3'b1;
    end
end
wire button_en = button_cnt == 3'd5;
///第二上升沿检测
integer l;
wire pos_edge_2;
reg [2:0] sig_2 [2:0];
always @ (posedge clk or posedge rst) begin
    if(rst) for (l=0;l<3;l=l+1) sig_2[l] <= 1'b0;
    else begin
    sig_2[2] <= sig_2[1];
    sig_2[1] <= sig_2[0];
    sig_2[0] <= button_en;
    end
end
assign pos_edge_2 = ~sig_2[2] & sig_2[1];
///计数加1
reg [6:0] button_count;
always @(posedge clk or posedge rst) begin
    if(rst) button_count <= 7'b0;
    else if(pos_edge_2) button_count <= button_count + 7'b1;
end
///显示
integer k;
always @(posedge clk or posedge rst) begin
    if(rst) begin
        display[3] <= 4'h0;
        display[2] <= 4'h0;
    end
    else begin
        for(k=0;k<10;k=k+1) begin
            if(button_count%100<10*(k+1) & button_count%100>=10*k) begin
                display[3] <= k;
                display[2] <= button_count%100 - 10*k;
            end
        end
    end
end

//计数器
///0.1s计数间隔
reg [31:0] cal_cnt = 32'b0;
reg cal_cnt_inc;
wire cal_cnt_end = cal_cnt_inc & cal_cnt == 50*N-2;
always @(posedge clk or posedge rst) begin
    if(rst) cal_cnt_inc <= 1'b0;
    else if(cal_rst) cal_cnt_inc <= 1'b0;
    else if(cal_cnt_end) cal_cnt_inc <= 1'b0;          
    else cal_cnt_inc <= 1'b1;     
end
always @(posedge clk or posedge rst) begin
    if(rst) cal_cnt <= 32'b0;        
    else if(cal_rst) cal_cnt <= 32'b0;
    else if(cal_cnt_end) cal_cnt <= 32'b0;       
    else if(cal_cnt_inc) cal_cnt <= cal_cnt + 32'b1;
end
///计数到20
reg [5:0] cal_count;
reg [5:0] cal_count_max = 5'd20;
reg cal_count_inc;
wire cal_count_end = cal_count_inc & cal_count == cal_count_max;
always @(posedge clk or posedge rst) begin
    if(rst) cal_count_inc <= 1'b0;
    else if(cal_rst) cal_count_inc <= 1'b0;
    else if(cal_count_end) cal_count_inc <= 1'b0;          
    else cal_count_inc <= 1'b1;     
end
always @(posedge clk or posedge rst) begin
    if(rst) cal_count <= 5'b1;
    else if(cal_rst) cal_count <= 5'b1;
    else if(cal_cnt_end) begin
        if(cal_count_end) cal_count <= 5'd20;
        else if(cal_count_inc) cal_count <= cal_count + 5'b1;
    end
end
///显示
always @(posedge clk or posedge rst) begin
    if(rst) begin
        display[1] <= 4'h0;
        display[0] <= 4'h0;
    end
    else if(cal_rst) begin
        display[1] <= 4'h0;
        display[0] <= 4'h0;
    end
    else begin
        if(cal_count<10) begin
            display[1] <= 4'h0;
            display[0] <= cal_count;
        end
        else if(cal_count<20) begin
            display[1] <= 4'h1;
            display[0] <= cal_count - 4'd10;
        end
        else begin
            display[1] <= 4'h2;
            display[0] <= 4'h0;
        end
    end
end

endmodule