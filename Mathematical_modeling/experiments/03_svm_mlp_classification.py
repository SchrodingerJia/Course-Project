import numpy as np
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# ========================
# 1. 准备数据集
# ========================
# OR数据集 (线性可分)
X_or = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_or = np.array([0, 1, 1, 1])
# XOR数据集 (线性不可分)
X_xor = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y_xor = np.array([0, 1, 1, 0])

# ========================
# 2. OR问题：线性SVM分类
# ========================
# 创建线性SVM模型
svm_or = LinearSVC(max_iter=5000)
svm_or.fit(X_or, y_or)
# 预测并评估
pred_or = svm_or.predict(X_or)
acc_or = accuracy_score(y_or, pred_or)
print("OR问题结果（线性SVM）:")
print(f"预测结果: {pred_or}")
print(f"准确率: {acc_or:.0%}")
print(f"决策函数: {svm_or.decision_function(X_or)}")
print(f"权重: {svm_or.coef_}, 偏置: {svm_or.intercept_}")

# 提取SVM参数
w = svm_or.coef_[0]  # 权重向量
b = svm_or.intercept_[0]  # 偏置项
# 构建分类函数
def svm_classifier(x1, x2):
    return w[0] * x1 + w[1] * x2 + b

# 可视化决策边界
plt.rcParams['axes.unicode_minus'] = False  # 显示负号
plt.figure(figsize=(8, 6))
plt.title("OR问题决策边界", fontsize=14)
# 绘制数据点
plt.scatter(X_or[y_or == 0, 0], X_or[y_or == 0, 1], s=100, label='0', marker='o')
plt.scatter(X_or[y_or == 1, 0], X_or[y_or == 1, 1], s=100, label='1', marker='s')
# 绘制决策边界
x_min, x_max = -0.5, 1.5
y_min, y_max = -0.5, 1.5
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 50),
                     np.linspace(y_min, y_max, 50))
Z = svm_classifier(xx.ravel(), yy.ravel()).reshape(xx.shape)
plt.contour(xx, yy, Z, levels=[0], colors='red', linewidths=2)
# 标注决策函数
plt.text(0.5, -0.2, f"决策函数: f(x) = {w[0]:.2f}·x1 + {w[1]:.2f}·x2 + {b:.2f}",
         fontsize=12, ha='center', bbox=dict(facecolor='white', alpha=0.8))
plt.xlabel("x1", fontsize=12)
plt.ylabel("x2", fontsize=12)
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.show()

# ========================
# 3. XOR问题：MLP分类
# ========================
# 创建MLP模型（单隐藏层含2个神经元）
mlp_xor = MLPClassifier(
    hidden_layer_sizes=(2,),  # 1个隐藏层，2个神经元
    activation='relu',        # ReLU激活函数
    solver='adam',            # 优化器
    max_iter=5000             # 最大迭代次数
)
mlp_xor.fit(X_xor, y_xor)
# 预测并评估
p_xor = mlp_xor.predict_proba(X_xor)
pred_xor = mlp_xor.predict(X_xor)
acc_xor = accuracy_score(y_xor, pred_xor)
print("XOR问题结果（MLP）:")
print(f"决策函数: {p_xor}")
print(f"预测结果: {pred_xor}")
print(f"准确率: {acc_xor:.0%}")
print(f"隐藏层权重矩阵:\n{mlp_xor.coefs_[0]}")
print(f"输出层权重: {mlp_xor.coefs_[1].flatten()}")

# 提取MLP参数
W1 = mlp_xor.coefs_[0]  # 输入层到隐藏层权重 (2x2)
b1 = mlp_xor.intercepts_[0]  # 隐藏层偏置 (2,)
W2 = mlp_xor.coefs_[1]  # 隐藏层到输出层权重 (2x1)
b2 = mlp_xor.intercepts_[1][0]  # 输出层偏置
# 定义ReLU激活函数
def relu(x):
    return np.maximum(0, x)

def hf(x1, x2):
    h1 = relu(W1[0, 0] * x1 + W1[1, 0] * x2 + b1[0])
    h2 = relu(W1[0, 1] * x1 + W1[1, 1] * x2 + b1[1])
    return (h1, h2)

# 构建MLP分类器
def mlp_classifier(x1, x2):
    # 输入层
    inputs = np.array([x1, x2])
    # 隐藏层计算
    h1 = relu(W1[0, 0] * x1 + W1[1, 0] * x2 + b1[0])
    h2 = relu(W1[0, 1] * x1 + W1[1, 1] * x2 + b1[1])
    # 输出层计算
    output = W2[0] * h1 + W2[1] * h2 + b2
    # 返回原始输出值（未经过sigmoid）
    return output

# 可视化决策边界和隐藏层激活
plt.figure(figsize=(8, 6))
# 主决策边界图
plt.title("XOR问题决策边界", fontsize=15)
plt.scatter(X_xor[y_xor == 0, 0], X_xor[y_xor == 0, 1], s=100, label='0', marker='o')
plt.scatter(X_xor[y_xor == 1, 0], X_xor[y_xor == 1, 1], s=100, label='1', marker='s')
# 绘制决策边界
xx, yy = np.meshgrid(np.linspace(-0.5, 1.5, 100),
                     np.linspace(-0.5, 1.5, 100))
Z = np.array([mlp_classifier(x, y) for x, y in zip(xx.ravel(), yy.ravel())])
Z = Z.reshape(xx.shape)
plt.contour(xx, yy, Z, levels=[0], colors='red', linewidths=2)
# 标注函数表达式
plt.text(0.5, -0.2, "分类函数表达式:", fontsize=15, ha='center')
plt.text(0.5, -0.3, f"h1 = ReLU({W1[0, 0]:.2f}·x1 + {W1[1, 0]:.2f}·x2 + {b1[0]:.2f})", fontsize=15, ha='center')
plt.text(0.5, -0.4, f"h2 = ReLU({W1[0, 1]:.2f}·x1 + {W1[1, 1]:.2f}x2 + {b1[1]:.2f})", fontsize=15, ha='center')
plt.text(0.5, -0.5, f"输出 = {W2[0, 0]:.2f}*h1 + {W2[1, 0]:.2f}*h2 + {b2:.2f}", fontsize=15, ha='center')
plt.tight_layout()
plt.show()
# 打印完整函数表达式
print("XOR问题MLP分类函数完整表达式:")
print(f"f(x1, x2) = {W2[0, 0]:.2f} * ReLU({W1[0, 0]:.2f}·x1 + {W1[1, 0]:.2f}·x2 + {b1[0]:.2f})")
print(f"          + {W2[1, 0]:.2f} * ReLU({W1[0, 1]:.2f}·x1 + {W1[1, 1]:.2f}·x2 + {b1[1]:.2f})")
print(f"          + {b2:.2f}")