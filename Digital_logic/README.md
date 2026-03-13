# 数字逻辑设计实验项目

## 项目简介
本项目为数字逻辑设计课程的实验部分，包含五个实验模块，涵盖了寄存器、计数器、数码管显示、UART通信以及综合应用等核心数字逻辑设计内容。所有代码使用Verilog HDL编写，适用于FPGA开发与仿真。

## 项目结构
```
.
├── lab-01-register/          # 实验一：寄存器
│   ├── pin.xdc              # 引脚约束文件
│   ├── reg8file.v           # 8位寄存器文件模块
│   └── testbench.v          # 测试文件
├── lab-02-counter/          # 实验二：计数器
│   ├── pin.xdc              # 引脚约束文件
│   ├── flowing_water_lights.v  # 流水灯控制模块
│   └── testbench.v          # 测试文件
├── lab-03-led-display/      # 实验三：数码管控制器
│   ├── pin.xdc              # 引脚约束文件
│   ├── led_display_ctrl.v   # LED显示控制模块
│   └── testbench.v          # 测试文件
├── lab-04-uart/            # 实验四：UART状态机
│   ├── pin.xdc              # 引脚约束文件
│   ├── uart.v              # UART顶层模块
│   ├── counter.v           # 计数器模块
│   ├── uart_send.v         # UART发送模块
│   └── testbench.v         # 测试文件
└── lab-05-integration/     # 实验五：综合实验
    ├── pin.xdc             # 引脚约束文件
    ├── calculator.v        # 计算器模块
    ├── calculator_tb.v     # 计算器测试文件
    ├── counter.v           # 计数器模块
    ├── displayer.v         # 显示模块
    ├── displayer_tb.v      # 显示测试文件
    ├── receive.v           # 接收模块
    ├── receive_tb.v        # 接收测试文件
    ├── send.v              # 发送模块
    ├── uart.v              # UART顶层模块
    ├── uart_receive_tb.v   # UART接收测试文件
    ├── uart_recv.v         # UART接收模块
    └── uart_send.v         # UART发送模块
```

## 实验内容

### 实验一：寄存器
实现一个8位寄存器文件，支持读写操作，包含写使能、写选择、读选择等功能。

### 实验二：计数器
设计一个可配置的计数器，支持不同频率和方向的流水灯效果。

### 实验三：数码管控制器
实现数码管显示控制器，能够将输入数据转换为对应的数码管段选信号。

### 实验四：UART状态机
设计UART通信的状态机，实现数据的串行发送功能。

### 实验五：综合实验
整合前四个实验的功能，实现一个完整的计算器系统，包含UART通信、计算逻辑和显示输出。

## 使用方法

### 仿真
1. 使用支持Verilog的仿真工具（如ModelSim、Vivado Simulator等）
2. 加载对应的testbench文件进行功能验证

### 综合与实现
1. 使用FPGA开发工具（如Vivado、Quartus等）
2. 导入对应实验的Verilog文件
3. 添加对应的pin.xdc引脚约束文件
4. 进行综合、实现并生成比特流文件
5. 下载到FPGA开发板进行验证

## 注意事项
1. 所有文件已进行匿名化处理，个人信息已替换为【NAME】和【ID】
2. 引脚约束文件针对特定FPGA开发板，使用前请根据实际硬件调整
3. 仿真时注意调整时钟周期和测试激励

## 开发环境
- 仿真工具：ModelSim / Vivado Simulator
- 综合工具：Vivado 2022.1 或更高版本
- 硬件平台：基于Xilinx Artix-7系列FPGA

## 许可证
本项目仅供学习参考使用。