import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
sns.set_palette("Set2")
data = {
    '企业': [f'企业{i+1}' for i in range(24)],
    '指标1': [-62.8,3.3,-120.8,-18.1,-3.8,-61.2,-20.3,-194.5,20.8,106.1,43,47,
              -3.3,35,46.7,20.8,33,26.1,68.6,37.3,-49.2,-19.2,40.6,34.6],
    '指标2': [-89.5,-3.5,103.2,-28.8,-50.6,-56.2,17.4,-25.8,-4.3,-22.9,16.4,16,
              4,20.8,12.6,12.5,23.6,10.4,13.8,33.4,-17.2,-36.7,5.8,26.4],
    '指标3': [1.7,1.1,2.5,1.1,0.9,1.7,1,0.5,1,1.5,1.3,1.9,
              2.7,1.9,0.9,2.4,1.5,2.1,1.6,3.5,0.3,0.8,1.8,1.8],
    '评估结果': [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
}
# 创建DataFrame
df = pd.DataFrame(data)
# 转换评估结果为二元变量 (0=破产, 1=可贷款)
df['target'] = df['评估结果'].apply(lambda x: 1 if x == 1 else (0 if x == -1 else np.nan))
# 分割数据集
train_df = df.iloc[:20].copy()
test_df = df.iloc[20:].copy()
# 添加常数项
train_df = sm.add_constant(train_df)
test_df = sm.add_constant(test_df)
# 定义模型公式
formula = 'target ~ 指标1 + 指标2 + 指标3'
# 1. Logistic回归模型
print("="*50)
print("Logistic回归模型结果")
print("="*50)
logit_model = sm.Logit.from_formula(formula, train_df).fit(disp=0)
print(logit_model.summary())
# 预测概率
train_df['logit_prob'] = logit_model.predict(train_df)
train_df['logit_pred'] = (train_df['logit_prob'] > 0.5).astype(int)
test_df['logit_prob'] = logit_model.predict(test_df)
test_df['logit_pred'] = (test_df['logit_prob'] > 0.5).astype(int)
# 2. Probit回归模型
print("\n" + "="*50)
print("Probit回归模型结果")
print("="*50)
probit_model = sm.Probit.from_formula(formula, train_df).fit(disp=0)
print(probit_model.summary())
# 预测概率
train_df['probit_prob'] = probit_model.predict(train_df)
train_df['probit_pred'] = (train_df['probit_prob'] > 0.5).astype(int)
test_df['probit_prob'] = probit_model.predict(test_df)
test_df['probit_pred'] = (test_df['probit_prob'] > 0.5).astype(int)
# 3. 模型评估
def evaluate_model(y_true, y_pred, model_name):
    """评估模型性能"""
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    print(f"\n{model_name}模型性能:")
    print(f"准确率: {accuracy:.4f}")
    print(f"精确率: {precision:.4f}")
    print(f"召回率: {recall:.4f}")
    print(f"F1分数: {f1:.4f}")
    print("混淆矩阵:")
    print(cm)
    return cm
# 评估Logistic模型
cm_logit = evaluate_model(train_df['target'], train_df['logit_pred'], "Logistic")
# 评估Probit模型
cm_probit = evaluate_model(train_df['target'], train_df['probit_pred'], "Probit")
# 4. 预测结果输出
print("\n" + "="*50)
print("企业贷款评估预测结果")
print("="*50)
# 创建结果DataFrame
result_df = test_df[['企业', '指标1', '指标2', '指标3']].copy()
result_df['Logistic概率'] = test_df['logit_prob']
result_df['Logistic预测'] = test_df['logit_pred'].map({1: '可贷款', 0: '破产'})
result_df['Probit概率'] = test_df['probit_prob']
result_df['Probit预测'] = test_df['probit_pred'].map({1: '可贷款', 0: '破产'})
# 添加决策差异标记
result_df['决策一致'] = result_df['Logistic预测'] == result_df['Probit预测']
print(result_df.round(4))
# 5. ROC曲线比较
plt.figure(figsize=(10, 8))
# Logistic ROC
fpr_logit, tpr_logit, _ = roc_curve(train_df['target'], train_df['logit_prob'])
roc_auc_logit = auc(fpr_logit, tpr_logit)
plt.plot(fpr_logit, tpr_logit, lw=2, label=f'Logistic (AUC = {roc_auc_logit:.2f})')
# Probit ROC
fpr_probit, tpr_probit, _ = roc_curve(train_df['target'], train_df['probit_prob'])
roc_auc_probit = auc(fpr_probit, tpr_probit)
plt.plot(fpr_probit, tpr_probit, lw=2, label=f'Probit (AUC = {roc_auc_probit:.2f})')
# 随机猜测线
plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假阳性率', fontsize=12)
plt.ylabel('真阳性率', fontsize=12)
plt.title('ROC曲线比较', fontsize=15)
plt.legend(loc="lower right", fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()