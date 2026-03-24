# 图像分割实验项目

本项目实现了四种经典的图像分割模型，用于课程实验和算法研究。

## 项目结构

```
.
├── README.md
├── requirements.txt
├── models/                    # 模型实现
│   ├── cv_model.py          # CV模型
│   ├── rsf_model.py         # RSF模型
│   ├── lgac_model.py       # 自动结合局部与全局信息的活动轮廓模型
│   └── tcm_model.py        # 结合先验约束项的图像分割模型
├── utils/                   # 工具函数
│   ├── data_loader.py      # 数据加载
│   └── plot_utils.py      # 可视化
├── scripts/                 # 测试脚本
│   ├── test_models.py   # 测试前三种模型
│   └── test_tcm.py     # 测试先验约束模型
├── data/                   # 数据
│   ├── images/
│   │   ├── cv_rsf/    # CV和RSF实验图像
│   │   └── tcm/        # 先验约束实验图像
│   └── labels/          # 标签数据
└── results/               # 结果输出目录
    ├── CV/
    ├── RSF/
    ├── LGAC/
    └── TCM/
```

## 功能概述

1. **CV模型**：经典的Chan-Vese活动轮廓模型，基于全局强度拟合。
2. **RSF模型**：区域可扩展拟合模型，处理强度不均匀图像。
3. **LGAC模型**：自动结合局部与全局信息的活动轮廓模型，自适应调整权重。
4. **TCM模型**：结合先验约束项的图像分割模型，利用预分割信息。

## 使用方法

### 环境配置

```bash
pip install -r requirements.txt
```

### 运行测试

1. **测试前三种模型**：
   ```bash
   python scripts/test_models.py
   ```

2. **测试先验约束模型**：
   ```bash
   python scripts/test_tcm.py
   ```

### 自定义使用

参考 `scripts/` 目录下的示例代码，根据需要修改参数和输入数据。

## 注意事项

- 确保数据文件放置在正确的目录下。
- 结果将保存在 `results/` 目录的相应子文件夹中。
- 模型参数可根据具体图像进行调整。

## 依赖

- Python 3.7+
- numpy
- scipy
- scikit-image
- opencv-python
- matplotlib
- scikit-learn

详细依赖见 `requirements.txt`。