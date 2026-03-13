`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2024/10/12 11:47:02
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
reg clr;
reg en;
reg [0:7] d;
reg [2:0] wsel;
reg [2:0] rsel;
wire [0:7] q;

initial begin
    clr = 1'b1;
    en = 1'b0;
    clk = 0;
    wsel = 3'b000;
    rsel = 3'b000;
    d = 8'b00000000;
    
    #10;
    clr = 1'b0;
    en = 1'b1;
    wsel = 3'b001;
    rsel = 3'b000;
    d = 8'b00000001;
    
    #10;
    en = 1'b0;
    
    #10;
    en = 1'b1;
    wsel = 3'b011;
    d = 8'b00000011;
    
    #10;
    en = 1'b0;
    
    #10;
    rsel = 3'b001;
    
    #10;
    rsel = 3'b011;
    
    #10;
    clr = 1'b1;
    
    #10;
    rsel = 3'b001;
    
    #200
    $finish;
end

always #5 clk = ~clk;

reg8file u_reg8file(
    .clk(clk),
    .clr(clr),
    .en(en),
    .wsel(wsel),
    .rsel(rsel),
    .d(d),
    .q(q)
);

endmodule
