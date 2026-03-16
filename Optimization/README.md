# 最优化方法课程项目

## 项目简介
本项目实现了基于PRP（Polak-Ribière-Polyak）共轭梯度法的约束最优化求解器，并应用于支持向量机（SVM）分类问题。项目采用面向对象编程（OOP）设计，将核心算法、测试用例和实践应用分离，便于维护和扩展。

## 项目结构
```
项目根目录/
├── optimization_methods.py  # 最优化求解方法类
├── test_cases.py            # 测试用例
├── svm_application.py       # SVM实践应用
├── requirements.txt         # 依赖包列表
└── README.md                # 项目说明文档
```

## 功能模块

### 1. optimization_methods.py
包含核心优化算法类 `OptimizationSolver`，主要功能：
- **梯度计算**：数值方法计算目标函数梯度
- **Wolfe-Powell一维搜索**：确定最优步长
- **罚函数法**：处理等式和不等式约束
- **PRP共轭梯度法**：主优化算法
- **可视化工具**：3D曲面和优化过程绘图

### 2. test_cases.py
提供5个测试函数，涵盖无约束、等式约束和不等式约束问题：
1. Rosenbrock函数（无约束）
2. 二次函数组合（混合约束）
3. 指数函数（等式约束）
4. 三角函数（等式约束）
5. Rastrigin函数（高维无约束）

### 3. svm_application.py
支持向量机应用示例：
- 使用`cvxopt`求解标准SVM对偶问题
- 使用自研优化器求解SVM原问题
- 数据可视化与决策边界绘制

## 使用方法

### 环境配置
```bash
pip install -r requirements.txt
```

### 运行测试用例
```python
# 在test_cases.py中直接运行
python test_cases.py
```

### 运行SVM示例
```python
# 在svm_application.py中直接运行
python svm_application.py
```

### 自定义优化问题
```python
from optimization_methods import OptimizationSolver

# 定义目标函数
def objective(X):
    return X[0]**2 + X[1]**2

# 定义约束条件
def constraint1(X):
    return X[0] + X[1] - 1  # 等式约束

def constraint2(X):
    return X[0] - 2  # 不等式约束（≥0）

constraints = {
    'eq': (constraint1,),   # 等式约束列表
    'el': (constraint2,)    # 不等式约束列表
}

# 初始点
X0 = np.array([2.0, 3.0])

# 创建求解器实例并求解
solver = OptimizationSolver()
result = solver.PRP(objective, constraints, X0)
```

## 算法特点
1. **鲁棒性**：采用罚函数法处理各种约束类型
2. **自适应**：Wolfe-Powell条件确保步长合理性
3. **可视化**：提供3D优化过程可视化
4. **可扩展**：面向对象设计便于添加新算法

## 依赖包
- numpy：数值计算
- matplotlib：数据可视化
- scikit-learn：生成测试数据
- cvxopt：SVM对比求解
- seaborn：美化绘图

## 注意事项
1. 高维问题可能需要调整罚函数系数`factor`
2. 复杂约束建议先验证约束函数正确性
3. 可视化仅支持二维决策变量

## 作者
最优化方法课程项目

## 许可证
仅供学习使用