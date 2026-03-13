`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2024/10/15 10:55:44
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
reg button;
reg [1:0] freq_set;
reg dir_set;
wire [7:0] led;

initial begin
    clk = 0;
    rst = 1'b1;
    button = 1'b0;
    freq_set = 2'b00;
    dir_set = 1'b0;
    
    #10;
    rst = 1'b0;
    
    #10;
    button = 1'b1;
    #80 button = 1'b0;
    
    #16000;
    button = 1'b1;
    #80 button = 1'b0;
    #1000 freq_set = 2'b01;
    
    #1300;
    button = 1'b1;
    #80 button = 1'b0;
    
    #160000;
    dir_set = 1'b1;
    
    #160000;
    button = 1'b1;
    #80 button = 1'b0;
    
    #16000;
    rst = 1'b1;
    
    #10000;
    $finish;

end

always #5 clk = ~clk;

flowing_water_lights #(100) u_flowing_water_lights(
    .clk(clk),
    .rst(rst),
    .dir_set(dir_set),
    .freq_set(freq_set),
    .button(button),
    .led(led)
);
endmodule