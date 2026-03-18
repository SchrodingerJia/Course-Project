import numpy as np
import pandas as pd
from math import log
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import cross_val_score, GridSearchCV, KFold
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
import pydotplus

# 读取银行借贷数据集
def load_bank_data():
    # 读取训练集和测试集
    train_df = pd.read_excel("../data/loan_train.xls")
    test_df = pd.read_excel("../data/loan_test.xls")
    # 去除name_id列
    train_df = train_df.drop(['nameid'], axis=1)
    test_df = test_df.drop(['nameid'], axis=1)
    # 对revenue列进行离散化
    re = [0, 10000, 20000, 30000, 40000, 50000]
    train_df['revenue'] = pd.cut(train_df['revenue'], re, labels=False)
    test_df['revenue'] = pd.cut(test_df['revenue'], re, labels=False)
    print("训练集形状:", train_df.shape)
    print("测试集形状:", test_df.shape)
    print("\n训练集信息:")
    print(train_df.info())
    return train_df, test_df

# 定义节点类
class Node:
    def __init__(self, root=True, label=None, feature_name=None, feature=None):
        self.root = root
        self.label = label
        self.feature_name = feature_name
        self.feature = feature
        self.tree = {}
        self.result = {'label:': self.label, 'feature': self.feature, 'tree': self.tree}
    def __repr__(self):
        return '{}'.format(self.result)
    def add_node(self, val, node):
        self.tree[val] = node
    def predict(self, features):
        if self.root is True:
            return self.label
        if features[self.feature] not in self.tree:
            # 如果特征值不在训练集中出现过的值中，返回最常见的类别
            return self.label
        return self.tree[features[self.feature]].predict(features)

# 基于C4.5算法的决策树类
class DTree:
    def __init__(self, epsilon=0.1):
        self.epsilon = epsilon
        self._tree = {}
    # 计算熵
    def calc_ent(self, datasets):
        data_length = len(datasets)
        if data_length == 0:
            return 0
        label_count = {}
        for i in range(data_length):
            label = datasets[i][-1]
            if label not in label_count:
                label_count[label] = 0
            label_count[label] += 1
        ent = -sum([(p/data_length)*log(p/data_length, 2) for p in label_count.values() if p > 0])
        return ent
    # 计算条件熵
    def cond_ent(self, datasets, axis=0):
        data_length = len(datasets)
        feature_sets = {}
        for i in range(data_length):
            feature = datasets[i][axis]
            if feature not in feature_sets:
                feature_sets[feature] = []
            feature_sets[feature].append(datasets[i])
        cond_ent = sum([(len(p)/data_length)*self.calc_ent(p) for p in feature_sets.values()])
        return cond_ent
    # 计算信息增益
    def info_gain(self, ent, cond_ent):
        return ent - cond_ent
    # 计算特征A的固有值（用于信息增益比）
    def calc_intrinsic_value(self, datasets, axis=0):
        data_length = len(datasets)
        feature_sets = {}
        for i in range(data_length):
            feature = datasets[i][axis]
            if feature not in feature_sets:
                feature_sets[feature] = 0
            feature_sets[feature] += 1
        iv = -sum([(count/data_length)*log(count/data_length, 2) for count in feature_sets.values() if count > 0])
        return iv
    # 计算信息增益比（C4.5算法）
    def info_gain_ratio(self, datasets, axis=0):
        ent = self.calc_ent(datasets)
        cond_ent = self.cond_ent(datasets, axis)
        info_gain_val = self.info_gain(ent, cond_ent)
        iv = self.calc_intrinsic_value(datasets, axis)
        # 避免除零错误
        if iv == 0:
            return 0
        return info_gain_val / iv
    # 返回信息增益比最大的特征
    def info_gain_ratio_train(self, datasets):
        count = len(datasets[0]) - 1
        best_feature = []
        for c in range(count):
            c_info_gain_ratio = self.info_gain_ratio(datasets, axis=c)
            best_feature.append((c, c_info_gain_ratio))
        # 比较大小
        best_ = max(best_feature, key=lambda x: x[-1])
        return best_
    def train(self, train_data):
        """
        input:数据集D(DataFrame格式)，特征集A，阈值epsilon
        output:决策树T
        """
        _, y_train, features = train_data.iloc[:, :-1], train_data.iloc[:, -1], train_data.columns[:-1]
        # 如果所有实例属于同一类
        if len(y_train.value_counts()) == 1:
            return Node(root=True, label=y_train.iloc[0])
        # 如果没有特征了
        if len(features) == 0:
            return Node(root=True, label=y_train.value_counts().sort_values(ascending=False).index[0])
        # 选择信息增益比最大的特征
        max_feature, max_info_gain_ratio = self.info_gain_ratio_train(np.array(train_data))
        max_feature_name = features[max_feature]
        # 如果信息增益比小于阈值
        if max_info_gain_ratio < self.epsilon:
            return Node(root=True, label=y_train.value_counts().sort_values(ascending=False).index[0])
        node_tree = Node(root=False, feature_name=max_feature_name, feature=max_feature)
        feature_list = train_data[max_feature_name].value_counts().index
        for f in feature_list:
            sub_train_df = train_data.loc[train_data[max_feature_name] == f].drop([max_feature_name], axis=1)
            sub_tree = self.train(sub_train_df)
            node_tree.add_node(f, sub_tree)
        # 设置当前节点的默认标签（用于预测时遇到未见过的特征值）
        node_tree.label = y_train.value_counts().sort_values(ascending=False).index[0]
        return node_tree
    def fit(self, train_data):
        self._tree = self.train(train_data)
        return self._tree
    def predict(self, X_test):
        if isinstance(X_test, pd.DataFrame):
            X_test = X_test.values
        predictions = []
        for x in X_test:
            predictions.append(self._tree.predict(x))
        return predictions

# 自定义评估指标
def evaluate_model(y_true, y_pred):
    """
    计算精确率、召回率和F1值
    """
    # 转换为numpy数组
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    # 计算混淆矩阵
    TP = np.sum((y_true == 1) & (y_pred == 1))
    FP = np.sum((y_true == 0) & (y_pred == 1))
    FN = np.sum((y_true == 1) & (y_pred == 0))
    TN = np.sum((y_true == 0) & (y_pred == 0))
    # 计算精确率
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    # 计算召回率
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    # 计算F1值
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    # 计算准确率
    accuracy = (TP + TN) / len(y_true)
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'accuracy': accuracy,
        'confusion_matrix': [[TN, FP], [FN, TP]]
    }

# 主程序 - 任务一
def task1_manual_decision_tree():
    print("=" * 50)
    print("任务一：Python自编程实现决策树模型")
    print("=" * 50)
    # 加载数据
    train_df, test_df = load_bank_data()
    # 创建并训练决策树模型
    dt = DTree(epsilon=0.01)
    print("\n训练决策树模型中...")
    tree = dt.fit(train_df)
    print("决策树训练完成!")
    print("\n决策树结构:")
    print(tree)
    # 预测
    print("\n进行预测...")
    X_test = test_df.iloc[:, :-1]
    y_test = test_df.iloc[:, -1]
    y_pred = dt.predict(X_test)
    # 评估模型
    print("\n模型评估结果:")
    evaluation = evaluate_model(y_test, y_pred)
    print(f"精确率 (Precision): {evaluation['precision']:.4f}")
    print(f"召回率 (Recall): {evaluation['recall']:.4f}")
    print(f"F1值 (F1-Score): {evaluation['f1_score']:.4f}")
    print(f"准确率 (Accuracy): {evaluation['accuracy']:.4f}")
    print(f"混淆矩阵:")
    print(f"[[TN={evaluation['confusion_matrix'][0][0]}, FP={evaluation['confusion_matrix'][0][1]}],")
    print(f" [FN={evaluation['confusion_matrix'][1][0]}, TP={evaluation['confusion_matrix'][1][1]}]]")
    return dt, evaluation

# 任务二：使用Sklearn库
def task2_sklearn_decision_tree():
    print("\n" + "=" * 50)
    print("任务二：使用Sklearn库实现决策树模型")
    print("=" * 50)
    # 加载数据
    train_df, test_df = load_bank_data()
    # 准备特征和标签
    X_train = train_df.iloc[:, :-1]
    y_train = train_df.iloc[:, -1]
    X_test = test_df.iloc[:, :-1]
    y_test = test_df.iloc[:, -1]
    # 使用交叉验证选择最佳参数
    print("\n使用交叉验证进行参数调优...")
    # 定义参数网格
    param_grid = {
        'max_depth': [3, 5, 7, 10, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 5],
        'criterion': ['gini', 'entropy']
    }
    # 创建决策树分类器
    dt_clf = DecisionTreeClassifier(random_state=42)
    # 使用网格搜索和交叉验证
    kfold = KFold(n_splits=4, shuffle=True, random_state=42)
    grid_search = GridSearchCV(dt_clf, param_grid, cv=kfold, scoring='f1', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    print(f"最佳参数: {grid_search.best_params_}")
    print(f"最佳交叉验证分数: {grid_search.best_score_:.4f}")
    # 使用最佳参数训练最终模型
    best_dt = grid_search.best_estimator_
    best_dt.fit(X_train, y_train)
    # 预测
    y_pred = best_dt.predict(X_test)
    # 评估模型
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    print("\n模型在测试集上的评估结果:")
    print(f"精确率 (Precision): {precision:.4f}")
    print(f"召回率 (Recall): {recall:.4f}")
    print(f"F1值 (F1-Score): {f1:.4f}")
    print(f"准确率 (Accuracy): {accuracy:.4f}")
    print(f"混淆矩阵:")
    print(cm)
    # 绘制决策树
    print("\n绘制决策树...")
    try:
        feature_names = X_train.columns.tolist()
        class_names = ['不贷款', '贷款']
        dot_data = export_graphviz(
            best_dt,
            out_file=None,
            feature_names=feature_names,
            class_names=class_names,
            filled=True,
            rounded=True,
            special_characters=True,
            fontname="Microsoft YaHei"
        )
        graph = pydotplus.graph_from_dot_data(dot_data)
        graph.write_png("../data/bank_loan_decision_tree.png")
        print("决策树已保存为 '../data/bank_loan_decision_tree.png'")
    except Exception as e:
        print(f"绘制决策树时出错: {e}")
        print("请确保已安装Graphviz并正确配置环境变量")
    # 交叉验证结果分析
    print("\n交叉验证详细结果:")
    cv_scores = cross_val_score(best_dt, X_train, y_train, cv=kfold, scoring='f1')
    print(f"各折交叉验证F1分数: {cv_scores}")
    print(f"平均交叉验证F1分数: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    return best_dt, {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'accuracy': accuracy,
        'confusion_matrix': cm
    }

if __name__ == "__main__":
    # 执行任务一
    dt1, eval1 = task1_manual_decision_tree()
    # 执行任务二
    dt2, eval2 = task2_sklearn_decision_tree()