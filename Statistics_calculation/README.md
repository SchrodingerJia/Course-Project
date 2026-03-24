# 统计计算课程实验项目

## 项目简介

本项目为统计计算课程的实验作业，包含四个实验，涵盖了随机数生成、统计推断、回归分析以及重抽样方法等核心统计计算内容。项目使用R语言进行数据分析与可视化，旨在通过实践加深对统计计算方法的理解。

## 项目结构

```
.
├── README.md               # 项目说明文档
├── requirements.txt        # 依赖包列表
└── labs/                   # 实验代码目录
    ├── lab1_basic_statistics_and_plots.Rmd      # 实验1：基础统计与绘图
    ├── lab1_basic_statistics_and_plots.R        # 实验1的R脚本版本
    ├── lab2_statistical_inference.Rmd           # 实验2：统计推断
    ├── lab3_regression_analysis.Rmd             # 实验3：回归分析
    └── lab4_bootstrap_and_jackknife.Rmd         # 实验4：Bootstrap与Jackknife
```

## 实验内容概述

### 实验1：基础统计与绘图
- 生成t分布、F分布和混合正态分布的随机数
- 使用ggplot2进行数据可视化（散点图、直方图、密度曲线）
- 实现帕累托分布、瑞利分布和离散随机变量的抽样

### 实验2：统计推断
- 二维正态分布的抽样方法（条件分布法和变换抽样法）
- 非置换抽样分布
- 参数估计（矩估计和最大似然估计）
- 线性回归模型

### 实验3：回归分析
- 双样本参数估计
- 总体方差的区间估计
- 参数检验的数值计算
- 假设检验的统计功效
- 单样本拟合优度检验（卡方检验和K-S检验）

### 实验4：Bootstrap与Jackknife
- 重抽样方法的基本原理
- 方差估计与置信区间构建
- 偏差校正

## 使用方法

### 环境配置
1. 安装R（版本≥4.0.0）和RStudio
2. 安装所需R包：
   ```R
   install.packages(c("ggplot2", "dplyr", "tidyr", "reshape2", "gridExtra", "rticles", "MASS"))
   ```

### 运行实验
1. 打开对应的Rmd文件（位于`labs/`目录下）
2. 在RStudio中点击"Knit"按钮生成PDF报告
3. 或直接运行R脚本文件

### 生成报告
每个实验的Rmd文件都可以编译生成PDF格式的实验报告，报告中包含代码、结果和可视化图表。

## 依赖包

项目依赖的主要R包如下（详见`requirements.txt`）：
- ggplot2: 数据可视化
- dplyr/tidyr: 数据整理
- gridExtra: 图形布局
- rticles: 学术论文模板
- MASS: 多元统计分析

## 注意事项
1. 项目中所有个人身份信息已匿名化处理
2. 部分实验需要设置随机种子以保证结果可重现
3. 数据文件（.RData, .Rhistory）为辅助文件，包含工作环境状态
4. 建议在运行前先阅读代码注释，理解各步骤的统计含义

## 贡献

本项目为课程作业，主要用于学习参考。如有改进建议，欢迎提出。