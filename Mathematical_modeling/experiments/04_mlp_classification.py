import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                            confusion_matrix, roc_curve, auc)
np.random.seed(42)
# 加载数据
data = pd.read_excel('data/e4data.xlsx', index_col=0)
# print("原始数据概览:")
# print(data.head())
# 数据清洗
# 添加省份名称到索引
data.set_index('name', inplace=True)
# 创建标签列：1-20号为0类，21-27号为1类
data['label'] = data['type'] - 1
# 分离特征和标签
features = data[['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8']]
labels = data['label']
# 划分训练集(1-27号)和测试集(28-30号)
X_train = features.iloc[:27]  # 前27个省份
y_train = labels.iloc[:27]
X_test = features.iloc[27:]   # 最后3个省份
y_test = labels.iloc[27:]
print("\n训练集形状:", X_train.shape)
print("测试集形状:", X_test.shape)
# 数据标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
# 构建并训练MLP模型
# 创建MLP模型
mlp = MLPClassifier(
    hidden_layer_sizes=(64, 32),  # 两个隐藏层
    activation='relu',            # ReLU激活函数
    solver='adam',                # Adam优化器
    alpha=0.001,                  # L2正则化系数
    batch_size=8,                 # 小批量大小
    learning_rate_init=0.01,      # 初始学习率
    max_iter=1000,                # 最大迭代次数
    early_stopping=True,          # 早停机制
    n_iter_no_change=50,          # 早停耐心值
    random_state=42,
    verbose=True
)
# 训练模型
history = mlp.fit(X_train_scaled, y_train)
# 模型评估与可视化
# 训练集评估
y_train_pred = mlp.predict(X_train_scaled)
train_acc = accuracy_score(y_train, y_train_pred)
# 测试集预测
y_test_pred = mlp.predict(X_test_scaled)
y_test_prob = mlp.predict_proba(X_test_scaled)[:, 1]  # 预测概率
# 评估指标
print("\n" + "="*50)
print("模型评估报告")
print("="*50)
print(f"训练集准确率: {train_acc:.4f}")
print("\n训练集分类报告:")
print(classification_report(y_train, y_train_pred))
print("\n测试集省份预测结果:")
test_results = pd.DataFrame({
    '省份': X_test.index,
    '实际类别': y_test.map({0: '第一类', 1: '第二类'}),
    '预测类别': [('第一类' if p == 0 else '第二类') for p in y_test_pred],
    '第二类概率': y_test_prob.round(4)
})
print(test_results)
print(y_train_pred)
# 绘制损失函数曲线
plt.figure(figsize=(10, 6))
plt.plot(history.loss_curve_)
plt.title("训练损失函数收敛曲线", fontsize=14)
plt.xlabel("迭代次数", fontsize=12)
plt.ylabel("损失值", fontsize=12)
plt.grid(True)
plt.show()
# 绘制混淆矩阵
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_train, y_train_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['第一类', '第二类'],
            yticklabels=['第一类', '第二类'])
plt.title("训练集混淆矩阵", fontsize=14)
plt.xlabel("预测标签", fontsize=12)
plt.ylabel("真实标签", fontsize=12)
plt.show()
# 绘制ROC曲线
fpr, tpr, thresholds = roc_curve(y_train, mlp.predict_proba(X_train_scaled)[:, 1])
roc_auc = auc(fpr, tpr)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC曲线 (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假阳性率', fontsize=12)
plt.ylabel('真阳性率', fontsize=12)
plt.title('ROC曲线', fontsize=14)
plt.legend(loc="lower right")
plt.show()