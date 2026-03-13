# 大学物理与电子电路实验数据处理项目

本项目用于处理大学物理与电子电路实验的实验数据，提供数据计算、不确定度分析、物理量运算及图表绘制等功能。

## 项目结构

```
大物与电路实验/
├── utils/                    # 工具模块
│   ├── __init__.py
│   ├── units.py              # 单位类 Unit
│   ├── useful_numbers.py     # 有效数字类 Usefulnum 和不确定度类 Uncertainty
│   ├── physics_quantity.py   # 带不确定度的物理量类 Physicsnum
│   ├── data_processing.py    # 数据处理函数（均值、方差、逐差法等）
│   └── plotting.py           # 绘图函数（散点图、拟合线、波形图等）
├── experiment_results/       # 各实验数据处理脚本
│   ├── __init__.py
│   ├── 1_liquid_surface_tension.py      # 液体表面张力实验
│   ├── 2_rlc_circuit.py                 # RLC电路实验
│   ├── 3_circuit_experiment_1.py        # 电路实验一（U-I特性）
│   ├── 4_youngs_modulus.py              # 杨氏模量实验
│   ├── 5_circuit_experiment_2.py        # 电路实验二（U-I特性）
│   ├── 6_circuit_experiment_4.py        # 电路实验四（交流电路波形）
│   ├── 7_analog_circuit_1.py            # 模电实验一（减法器、积分器、微分器）
│   ├── 8_analog_circuit_2.py            # 模电实验二（波形发生器）
│   └── 9_analog_circuit_3.py            # 模电实验三（磁滞回线）
├── requirements.txt          # 项目依赖
└── README.md                 # 项目说明
```

## 功能模块说明

### utils 模块
- **units.py**: 定义 `Unit` 类，支持物理单位的解析、运算（乘、除、幂、开方）及标准化输出。
- **useful_numbers.py**: 定义 `Usefulnum`（有效数字）和 `Uncertainty`（不确定度）类，用于科学计数法表示和修约。
- **physics_quantity.py**: 定义 `Physicsnum` 类，表示带不确定度的物理量，支持加减乘除、幂运算及自动单位推导。
- **data_processing.py**: 提供常用数据处理函数，如均值、方差、标准差、逐差法、列表变换等。
- **plotting.py**: 提供多种绘图函数，支持散点图、线性拟合、多曲线对比、波形绘制等。

### experiment_results 模块
包含多个独立实验的数据处理脚本，每个脚本对应一个具体实验，直接调用 utils 中的工具完成计算与绘图。

## 使用方法

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **运行实验脚本**：
   进入 `experiment_results/` 目录，直接运行对应的 Python 文件，例如：
   ```bash
   python 1_liquid_surface_tension.py
   ```
   脚本将自动计算并输出物理量结果，同时显示相关图表。

3. **自定义实验**：
   可参考现有脚本，利用 utils 中的类与函数编写新的实验数据处理程序。

## 依赖库

- numpy
- matplotlib
- openpyxl（如需处理 Excel 数据）

详见 `requirements.txt`。

## 注意事项

- 本项目代码由 Jupyter Notebook 重构而来，保留了原有的计算逻辑与输出格式。
- 物理量运算时会自动处理单位与不确定度传播。
- 绘图函数默认显示图像，可根据需要调整参数或保存图像。

## 作者

本项目为大学物理与电子电路实验数据处理工具集，适用于实验报告的数据处理与图表生成。