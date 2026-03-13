`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2024/11/06 14:32:04
// Design Name: 
// Module Name: testbench
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


module testbench(
    );

reg clk;
reg rst;
reg start;
wire uart_tx;

UART #(10000000) u_UART(
    .clk(clk),
    .rst(rst),
    .start(start),
    .uart_tx(uart_tx)
);

always #5 clk = ~clk;

initial begin
    clk = 0;
    rst = 1'b1;
    start = 1'b0;
    
    #30;
    rst = 1'b0;
    
    #20;
    start = 1'b1;
    #50 start = 1'b0;
    
    #32000000;
    $finish;
end

endmodule
