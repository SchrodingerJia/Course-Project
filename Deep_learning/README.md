# 深度学习课程实验项目

## 项目概述
本项目包含四个深度学习实验，涵盖了从基础神经网络到高级图像处理的应用。每个实验都针对特定的学习目标设计，包括MNIST手写数字识别、神经网络优化实验、猫狗图像分类以及双能谱图像去噪。

## 项目结构
```
code/
├── lab1/                    # 实验一：MNIST手写数字识别
│   └── mnist_learning.py
├── lab2/                    # 实验二：神经网络优化实验
│   └── neural_network_experiment.py
├── lab3/                    # 实验三：猫狗图像分类
│   ├── task1_optimization.py          # 优化器对比实验
│   ├── task2_hyperparameter_tuning.py # 超参数调优
│   └── task3_model_evaluation.py      # 模型评估与可视化
├── lab4/                    # 实验四：双能谱图像去噪
│   └── task4_dual_energy_denoising.py
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明
```

## 实验内容

### 实验一：MNIST手写数字识别
- **文件**: `lab1/mnist_learning.py`
- **功能**: 使用PyTorch实现基础的MNIST手写数字识别
- **学习目标**: 掌握PyTorch基础操作、数据加载、简单神经网络构建

### 实验二：神经网络优化实验
- **文件**: `lab2/neural_network_experiment.py`
- **功能**: 对比不同优化器（SGD、Adam、RMSProp）的性能
- **学习目标**: 理解不同优化算法的原理和适用场景

### 实验三：猫狗图像分类
- **任务一**: 优化器对比实验 (`task1_optimization.py`)
  - 对比不同优化器在猫狗分类任务上的表现
  
- **任务二**: 超参数调优 (`task2_hyperparameter_tuning.py`)
  - 使用网格搜索和交叉验证进行系统化超参数优化
  - 支持多GPU并行训练
  
- **任务三**: 模型评估与可视化 (`task3_model_evaluation.py`)
  - 模型性能可视化
  - 混淆矩阵分析
  - 错误样本分析

### 实验四：双能谱图像去噪
- **文件**: `lab4/task4_dual_energy_denoising.py`
- **功能**: 基于U-Net架构的双能谱图像去噪网络
- **特点**:
  - 支持双通道图像处理
  - 残差连接设计
  - 完整的训练、验证、测试流程
  - 结果可视化功能

## 环境要求

### 硬件要求
- CPU: 4核以上
- 内存: 8GB以上
- GPU: 支持CUDA的NVIDIA GPU（可选，推荐用于训练加速）

### 软件依赖
详见 `requirements.txt` 文件，主要依赖包括：
- Python 3.8+
- PyTorch 1.10+
- torchvision
- numpy
- matplotlib
- scikit-learn
- seaborn
- pandas

## 使用方法

### 1. 环境配置
```bash
# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行实验

#### 实验一：MNIST手写数字识别
```bash
cd code
python lab1/mnist_learning.py
```

#### 实验二：神经网络优化实验
```bash
cd code
python lab2/neural_network_experiment.py
```

#### 实验三：猫狗图像分类
```bash
# 任务一：优化器对比
cd code
python lab3/task1_optimization.py

# 任务二：超参数调优
python lab3/task2_hyperparameter_tuning.py

# 任务三：模型评估
python lab3/task3_model_evaluation.py
```

#### 实验四：双能谱图像去噪
```bash
cd code
python lab4/task4_dual_energy_denoising.py
```

### 3. 数据准备
- 实验一：MNIST数据集自动下载
- 实验二：使用内置数据集
- 实验三：需要准备猫狗图像数据集，结构如下：
  ```
  data-cat-dog/
  ├── training_data/
  │   ├── cat/
  │   └── dog/
  └── testing_data/
      ├── cat/
      └── dog/
  ```
- 实验四：需要准备双能谱图像数据集（.npy格式）

## 项目特点

1. **模块化设计**: 每个实验独立，便于理解和复用
2. **代码规范**: 遵循PEP8编码规范，注释详细
3. **性能优化**: 支持多GPU训练、混合精度训练等高级特性
4. **可视化完善**: 提供丰富的训练过程可视化和结果分析
5. **可扩展性**: 易于添加新的实验或修改现有模型

## 注意事项

1. 运行前请确保已安装所有依赖包
2. GPU训练需要正确配置CUDA环境
3. 实验三需要提前准备猫狗图像数据集
4. 实验四需要准备相应的双能谱图像数据
5. 部分实验可能需要较长的训练时间，建议在GPU环境下运行

## 结果文件

每个实验运行后会生成相应的结果文件：
- 模型文件（.pth格式）
- 训练过程图表（.png格式）
- 性能评估报告
- 可视化结果

## 许可证

本项目仅供学习使用。