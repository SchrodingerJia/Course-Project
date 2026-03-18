 
# 数据预处理
import pandas as pd
from datetime import datetime
 
def preprocess_data(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path).dropna()
    # 将LAST_VISITS转换为datetime类型
    df['LAST_VISITS'] = pd.to_datetime(df['LAST_VISITS'])
    # 观测窗口结束时间
    end_date = datetime(2025, 9, 1)
    # 按USER_ID分组计算各项指标
    result = df.groupby('USER_ID').agg({
        'ACCOUNT': lambda x: x.mode().iloc[0],  # 客户名称众数
        'type': lambda x: x.mode().iloc[0],     # 客户类型众数
        'LAST_VISITS': ['count', 'max'],        # 计算用餐次数和最近用餐时间
        'number_consumers': 'sum',              # 总用餐人数
        'expenditure': 'sum'                    # 总消费金额
    }).reset_index()
    # 重命名列
    result.columns = ['USER_ID', 'ACCOUNT', 'type', 'frequence', 'last_visit', 'total_consumers', 'amount']
    # 计算recently（距离观测窗口结束的天数）
    result['recently'] = (end_date - result['last_visit']).dt.days
    # 计算average（人均消费金额）
    result['average'] = (result['amount'] / result['total_consumers']).round(2)
    # 选择需要的列
    return result[['USER_ID', 'ACCOUNT', 'type', 'frequence', 'recently', 'average', 'amount']]
 
 
train_file = "../data/train.csv"
test_file = "../data/test.csv"
processed_train = preprocess_data(train_file)
processed_test = preprocess_data(test_file)
print(processed_train.head())
processed_train.to_csv("../data/processed_train.csv", index=False)
processed_test.to_csv("../data/processed_test.csv", index=False)
 
 
# 支持向量机预测
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
 
 
# 1. 比较不同核函数的分类准确率
def compare_kernels(X_train, y_train, X_test, y_test):
    kernels = ['linear', 'poly', 'rbf', 'sigmoid']
    accuracies = {}
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    for kernel in kernels:
        svm = SVC(decision_function_shape='ovo', kernel=kernel)
        svm.fit(X_train_scaled, y_train)
        y_pred_scaled = svm.predict(X_test_scaled)
        accuracies[kernel] = accuracy_score(y_test, y_pred_scaled)
    return accuracies
# 2. 数据标准化对模型的影响
def standardization_effect(X_train, y_train, X_test, y_test):
    # 不使用标准化
    svm = SVC(decision_function_shape='ovo', kernel='rbf')
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    accuracy_without = accuracy_score(y_test, y_pred)
    # 使用标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    svm_scaled = SVC(decision_function_shape='ovo', kernel='rbf')
    svm_scaled.fit(X_train_scaled, y_train)
    y_pred_scaled = svm_scaled.predict(X_test_scaled)
    accuracy_with = accuracy_score(y_test, y_pred_scaled)
    return accuracy_without, accuracy_with
# 3. 高斯核函数和多项式核函数的参数调整
def tune_kernel_parameters(X_train, y_train):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    # 高斯核参数
    param_grid_rbf = {
        'C':[0.01, 0.1, 1, 10, 100],
        'gamma': ['scale', 0.01, 0.1]
    }
    # 多项式核参数
    param_grid_poly = {
        'C':[0.01, 0.1, 1, 10, 100],
        'degree': [2, 3, 4],
        'gamma': ['scale', 0.01, 0.1]
    }
    # 网格搜索
    grid_rbf = GridSearchCV(SVC(decision_function_shape='ovo', kernel='rbf'), param_grid_rbf, cv=4, scoring='accuracy')
    grid_poly = GridSearchCV(SVC(decision_function_shape='ovo', kernel='poly'), param_grid_poly, cv=4, scoring='accuracy')
    grid_rbf.fit(X_train_scaled, y_train)
    grid_poly.fit(X_train_scaled, y_train)
    return grid_rbf.best_params_, grid_rbf.best_score_, grid_poly.best_params_, grid_poly.best_score_
# 4. 松弛系数惩罚项C的调整
def tune_C_parameter(X_train, y_train):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    param_grid = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100]
    }
    grid = GridSearchCV(SVC(decision_function_shape='ovo', kernel='rbf'), param_grid, cv=4, scoring='accuracy')
    grid.fit(X_train_scaled, y_train)
    return grid.best_params_, grid.best_score_
 
 
# 准备训练数据和测试数据
processed_train = pd.read_csv("../data/processed_train.csv")
processed_test = pd.read_csv("../data/processed_test.csv")
X_train = processed_train[['frequence', 'recently', 'average', 'amount']]
y_train = processed_train['type']
X_test = processed_test[['frequence', 'recently', 'average', 'amount']]
y_test = processed_test['type']
 
 
# 执行分析
print("1. 不同核函数的分类准确率:")
accuracies = compare_kernels(X_train, y_train, X_test, y_test)
for kernel, acc in accuracies.items():
    print(f"{kernel}: {acc:.4f}")
 
 
print("2. 数据标准化对模型的影响:")
acc_without, acc_with = standardization_effect(X_train, y_train, X_test, y_test)
print(f"不使用标准化: {acc_without:.4f}")
print(f"使用标准化: {acc_with:.4f}")
 
 
print("3. 高斯核和多项式核参数调整:")
best_params_rbf, best_score_rbf, best_params_poly, best_score_poly = tune_kernel_parameters(X_train, y_train)
print(f"高斯核最佳参数: {best_params_rbf}, 最佳准确率: {best_score_rbf:.4f}")
print(f"多项式核最佳参数: {best_params_poly}, 最佳准确率: {best_score_poly:.4f}")
 
 
print("4. 松弛系数C的调整:")
best_params_C, best_score_C = tune_C_parameter(X_train, y_train)
print(f"最佳C值: {best_params_C}, 最佳准确率: {best_score_C:.4f}")
 
 
print("最佳模型:")
best_model = SVC(decision_function_shape='ovo', kernel='rbf', gamma = best_params_rbf['gamma'], C=best_params_C['C'])
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
best_model.fit(X_train_scaled, y_train)
print(f"训练集准确率: {accuracy_score(y_train, best_model.predict(X_train_scaled)):.4f}")
print(f"测试集准确率: {accuracy_score(y_test, best_model.predict(X_test_scaled)):.4f}")
 
 
# 感知机模型预测
 
 
from sklearn.linear_model import Perceptron
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
 
 
def train_perceptron(X_train, y_train, X_test, y_test):
    # 定义参数网格
    param_grid = {
        'eta0': [0.001, 0.01, 0.1, 1.0],  # 学习率
        'max_iter': [100, 500, 1000, 2000],  # 最大迭代次数
        'penalty': [None, 'l2', 'l1', 'elasticnet']  # 惩罚项
    }
    # 创建感知机模型
    perceptron = Perceptron(random_state=42)
    # 网格搜索
    grid_search = GridSearchCV(perceptron, param_grid, cv=4, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    # 最佳模型
    best_perceptron = grid_search.best_estimator_
    # 预测
    y_pred = best_perceptron.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return {
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'test_accuracy': accuracy,
        'model': best_perceptron
    }
 
 
perceptron_results = train_perceptron(X_train, y_train, X_test, y_test)
print(f"最佳参数: {perceptron_results['best_params']}")
print(f"交叉验证最佳准确率: {perceptron_results['best_score']:.4f}")
print(f"测试集准确率: {perceptron_results['test_accuracy']:.4f}")
 
 
# 决策树模型预测
 
 
from sklearn.tree import DecisionTreeClassifier, export_graphviz
import pydotplus
 
 
def train_decision_tree(X_train, y_train, X_test, y_test):
    # 定义参数网格
    param_grid = {
        'max_depth': [3, 5, 7, 9, None],  # 树的最大深度
        'min_samples_split': [2, 5, 10],  # 内部节点再划分所需最小样本数
        'min_samples_leaf': [1, 2, 4],  # 叶节点最少样本数
        'criterion': ['gini', 'entropy']  # 分裂标准
    }
    # 创建决策树模型
    dt = DecisionTreeClassifier(random_state=42)
    # 网格搜索
    grid_search = GridSearchCV(dt, param_grid, cv=4, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    # 最佳模型
    best_dt = grid_search.best_estimator_
    # 预测
    y_pred = best_dt.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return {
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'test_accuracy': accuracy,
        'model': best_dt
    }
# 决策树可视化
def visualize_decision_tree(model, feature_names, class_names, filename='decision_tree.png'):
    dot_data = export_graphviz(
        model,
        out_file=None,
        feature_names=feature_names,
        class_names=class_names,
        filled=True,
        rounded=True,
        special_characters=True
    )
    graph = pydotplus.graph_from_dot_data(dot_data)
    graph.write_png(filename)
    return filename
 
 
dt_results = train_decision_tree(X_train, y_train, X_test, y_test)
print(f"最佳参数: {dt_results['best_params']}")
print(f"交叉验证最佳准确率: {dt_results['best_score']:.4f}")
print(f"测试集准确率: {dt_results['test_accuracy']:.4f}")
 
 
feature_names = ['frequence', 'recently', 'average', 'amount']
class_names = ['Quasi-loss', 'Non-loss']
tree_image = visualize_decision_tree(
    dt_results['model'],
    feature_names,
    class_names,
    'customer_churn_decision_tree.png'
)
print(f"\n决策树已保存为: {tree_image}")
 