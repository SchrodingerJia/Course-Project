# 数学建模课程实验项目

## 项目简介

本项目为数学建模课程实验，包含多个经典的数学建模与机器学习实验案例。项目已从原始的Jupyter Notebook格式重构为模块化的Python脚本，便于管理和复用。

## 项目结构

```
数学建模/
├── data/                   # 数据目录
│   └── e4data.xlsx         # 实验4数据集
├── experiments/            # 实验代码目录
│   ├── 01_grey_prediction.py              # 实验1：灰色预测模型
│   ├── 02_logistic_probit_regression.py   # 实验2：Logistic与Probit回归
│   ├── 03_svm_mlp_classification.py       # 实验3：SVM与MLP分类
│   └── 04_mlp_classification.py           # 实验4：MLP神经网络分类
├── requirements.txt        # 项目依赖
└── README.md               # 项目说明文档
```

## 实验内容

### 实验1：灰色预测模型
- **文件**: `experiments/01_grey_prediction.py`
- **内容**: 实现GM(1,1)和GM(2,1)灰色预测模型，用于时间序列预测
- **功能**: 级比检验、模型参数估计、未来值预测、误差分析

### 实验2：Logistic与Probit回归
- **文件**: `experiments/02_logistic_probit_regression.py`
- **内容**: 企业贷款风险评估，比较Logistic回归和Probit回归模型
- **功能**: 二元分类、模型训练与评估、ROC曲线分析、预测结果输出

### 实验3：SVM与MLP分类
- **文件**: `experiments/03_svm_mlp_classification.py`
- **内容**: OR和XOR问题的分类器实现，比较线性SVM和MLP神经网络
- **功能**: 线性/非线性分类、决策边界可视化、模型参数解析

### 实验4：MLP神经网络分类
- **文件**: `experiments/04_mlp_classification.py`
- **内容**: 基于多层感知机的省份分类问题
- **功能**: 数据标准化、神经网络训练、性能评估、损失曲线与ROC曲线可视化

## 使用方法

1. **环境配置**:
   ```bash
   pip install -r requirements.txt
   ```

2. **运行实验**:
   直接运行对应的Python脚本即可：
   ```bash
   python experiments/01_grey_prediction.py
   python experiments/02_logistic_probit_regression.py
   python experiments/03_svm_mlp_classification.py
   python experiments/04_mlp_classification.py
   ```

3. **查看结果**:
   每个实验都会在控制台输出详细的模型结果和评估指标，并生成相应的可视化图表。

## 依赖环境

项目依赖的主要Python库：
- numpy
- pandas
- matplotlib
- seaborn
- scikit-learn
- statsmodels
- sympy

详细版本要求见`requirements.txt`文件。

## 注意事项

1. 所有实验数据已内置或放置在`data/`目录下
2. 项目结构清晰，便于扩展新的实验模块
3. 每个实验文件都是独立的，可以单独运行

## 贡献

本项目为课程实验项目，主要用于学习和教学目的。如有改进建议，欢迎提出。