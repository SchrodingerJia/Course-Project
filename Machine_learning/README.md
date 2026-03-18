# 统计机器学习实验项目

## 项目概述

本项目为统计机器学习课程的实验项目，包含六个实验内容，涵盖了数据预处理、可视化、经典机器学习算法实现与应用等多个方面。项目已按照模块化、规范化的要求进行重构，便于学习、复现和扩展。

## 项目结构

```
实验项目/
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖包列表
├── experiment_01/               # 实验一：数据预处理与可视化
│   ├── experiment_01_main.py    # 主程序：学生成绩数据分析
│   ├── data_processing/         # 数据处理示例代码
│   │   ├── numpy_example.py     # Numpy使用示例
│   │   ├── pandas_example.py    # Pandas使用示例
│   │   ├── numpy_pandas_example.py  # Numpy和Pandas综合应用
│   │   ├── matplotlib_example.py    # Matplotlib使用示例
│   │   └── sklearn_example.py   # Scikit-learn使用示例
│   └── data/                    # 实验数据
│       ├── report_card_1.txt    # 学生成绩数据1
│       ├── report_card_2.txt    # 学生成绩数据2
│       └── beijing_air_quality.xlsx  # 北京市空气质量数据
├── experiment_02/               # 实验二：感知机模型与鸢尾花分类
│   ├── experiment_02_main.py    # 主程序：感知机实现与比较
│   └── data/                    # 实验数据（使用内置数据集）
├── experiment_03/               # 实验三：决策树与银行借贷预测
│   ├── experiment_03_main.py    # 主程序：决策树模型实现
│   └── data/                    # 实验数据
│       ├── loan_train.xls       # 银行借贷训练集
│       ├── loan_test.xls        # 银行借贷测试集
│       └── bank_loan_decision_tree.png  # 决策树可视化结果
├── experiment_04/               # 实验四：空气质量预测
│   ├── experiment_04_main.py    # 主程序：空气质量分析
│   └── data/                    # 实验数据
│       ├── beijing_air_quality_train.xlsx  # 训练数据
│       └── beijing_air_quality_test.xlsx   # 测试数据
├── experiment_05/               # 实验五：支持向量机与客户流失预测
│   ├── experiment_05_main.py    # 主程序：SVM与感知机比较
│   └── data/                    # 实验数据
│       ├── train.csv            # 原始训练数据
│       ├── test.csv             # 原始测试数据
│       ├── processed_train.csv  # 预处理后训练数据
│       └── processed_test.csv   # 预处理后测试数据
└── experiment_06/               # 实验六：聚类分析与收入分类
    ├── experiment_06_main.py    # 主程序：K-means与层次聚类
    └── data/                    # 实验数据
        ├── rural_income_2020.xlsx      # 农村居民收入数据
        ├── consumption_data.xls        # 消费数据
        └── clustering_results.xlsx     # 聚类结果
```

## 实验内容简介

### 实验一：数据预处理与可视化
- **主要内容**：学生成绩数据的读取、合并、缺失值处理、异常值检测、特征工程、标准化处理
- **可视化方法**：箱线图、相关性热力图、平行坐标图、雷达图
- **技术要点**：Pandas数据处理、Matplotlib/Seaborn可视化

### 实验二：感知机模型与鸢尾花分类
- **主要内容**：手动实现感知机算法（随机梯度下降）、使用Sklearn库实现感知机
- **技术要点**：感知机原理、线性分类、特征选择、模型评估
- **思考题**：数据处理格式选择、特征选择方法、随机种子作用、学习率影响

### 实验三：决策树与银行借贷预测
- **主要内容**：手动实现C4.5决策树算法、使用Sklearn决策树
- **技术要点**：信息增益比计算、决策树构建、剪枝策略、模型评估指标
- **应用场景**：银行借贷风险评估

### 实验四：空气质量预测
- **主要内容**：北京市空气质量数据分析与预测
- **技术要点**：时间序列分析、特征工程、回归/分类模型

### 实验五：支持向量机与客户流失预测
- **主要内容**：支持向量机（SVM）原理与应用、感知机与决策树对比
- **技术要点**：核函数比较、参数调优、数据标准化影响、多模型比较
- **应用场景**：客户流失预测

### 实验六：聚类分析与收入分类
- **主要内容**：K-means聚类、层次聚类算法实现与比较
- **技术要点**：聚类算法原理、肘部法则、轮廓系数、聚类评估
- **应用场景**：农村居民收入水平分类

## 环境要求

### Python版本
- Python 3.7+

### 主要依赖包
```
numpy>=1.19.0
pandas>=1.1.0
matplotlib>=3.3.0
seaborn>=0.11.0
scikit-learn>=0.24.0
jupyter>=1.0.0
openpyxl>=3.0.0
xlrd>=2.0.0
pydotplus>=2.0.0
graphviz>=0.16.0
```

### 安装方法
1. 使用pip安装：
```bash
pip install -r requirements.txt
```

2. 如需使用决策树可视化功能，请确保系统已安装Graphviz：
   - **Windows**：从[Graphviz官网](https://graphviz.org/download/)下载安装包
   - **Linux**：`sudo apt-get install graphviz`
   - **Mac**：`brew install graphviz`

## 使用方法

### 运行单个实验
```bash
# 运行实验一
python experiment_01/experiment_01_main.py

# 运行实验二
python experiment_02/experiment_02_main.py

# 运行实验三
python experiment_03/experiment_03_main.py

# 运行实验四
python experiment_04/experiment_04_main.py

# 运行实验五
python experiment_05/experiment_05_main.py

# 运行实验六
python experiment_06/experiment_06_main.py
```

### 查看数据处理示例
```bash
# 查看Numpy示例
python experiment_01/data_processing/numpy_example.py

# 查看Pandas示例
python experiment_01/data_processing/pandas_example.py

# 查看Matplotlib示例
python experiment_01/data_processing/matplotlib_example.py
```

### 使用Jupyter Notebook（原始.ipynb文件已转换为.py）
所有原始.ipynb文件已转换为.py文件，可直接运行。如需使用Notebook环境，可将.py文件复制到Jupyter中执行。

## 项目特点

1. **模块化设计**：每个实验独立成文件夹，包含完整的数据和代码
2. **代码规范化**：文件命名使用英文小写+下划线，结构清晰
3. **功能完整**：包含数据预处理、模型实现、可视化、评估全流程
4. **可复现性**：固定随机种子，确保实验结果可复现

## 注意事项

1. 部分实验需要读取Excel文件，请确保已安装openpyxl或xlrd
2. 决策树可视化需要Graphviz支持，请提前安装配置
3. 数据文件路径已调整为相对路径，请勿移动文件位置
4. 所有输出结果（如图片、处理后的数据）将保存在各实验的data目录中

## 扩展建议

1. 可尝试修改模型参数，观察对结果的影响
2. 可添加新的评估指标或可视化方法
3. 可尝试将算法应用于其他数据集
4. 可优化代码性能，如使用向量化操作

## 许可证

本项目仅用于教学目的，请勿用于商业用途。
