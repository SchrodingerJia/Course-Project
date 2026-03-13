module testbench(

    );
reg clk;
reg rst;
reg cal_rst;
reg button;
reg [0:7] count;
wire [0:7] led_en;
wire [0:7] led_cx;

initial begin
    clk = 0;
    rst = 1'b1;
    cal_rst = 1'b1;
    button = 1'b0;
    count = 8'b0;
    
    #10;
    rst = 1'b0;
    cal_rst = 1'b0;
    
    //拨码开关测试
    #2000;
    count = 8'b10000000;
    #2000 count = 8'b11000000;
    #2000 count = 8'b11010000;
    #2000 count = 8'b11000110;
    
    //计数复位测试
    #100000;
    cal_rst = 1'b1;
    #10 cal_rst = 1'b0;
    
    //按键计数测试
    #100000;
    button = 1'b1;
    #1000 button = 1'b0;
    //模拟抖动
    #2000;
    button = 1'b1;
    #40 button = 1'b0;
    #30;
    button = 1'b1;
    #100 button = 1'b0;
    #50;
    button = 1'b1;
    #300 button = 1'b0;
    #80;
    button = 1'b1;
    #1000 button = 1'b0;
    
    #2000;
    $finish;
    
end
    
always #5 clk = ~clk;

led_display_ctrl #(10) u_led_display_ctrl(
    .clk(clk),
    .rst(rst),
    .button(button),
    .cal_rst(cal_rst),
    .count(count),
    .led_en(led_en),
    .led_cx(led_cx)
);
    
endmodule