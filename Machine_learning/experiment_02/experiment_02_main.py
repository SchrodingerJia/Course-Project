# 实验二：感知机模型与鸢尾花分类
# 作者: 【NAME】
# 学号: 【ID】

import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 数据准备与可视化
def prepare_and_visualize_data():
    """准备数据并进行可视化分析"""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['label'] = iris.target
    df.columns = ['sepal length', 'sepal width', 'petal length', 'petal width', 'label']
    
    # t-SNE降维可视化
    X = df.drop('label', axis=1)
    y = df['label']
    tsne = TSNE(n_components=2)
    X_tsne = tsne.fit_transform(X)
    
    plt.figure(figsize=(10, 8))
    colors = ['r', 'g', 'b']
    for i, label_name in enumerate(iris.target_names):
        mask = (y == i)
        plt.scatter(X_tsne[mask, 0], X_tsne[mask, 1], c=colors[i], label=label_name)
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.title('t-SNE visualization of Iris dataset')
    plt.legend()
    plt.show()
    
    # 原始数据可视化（前两个特征）
    plt.scatter(df[:50]['sepal length'], df[:50]['sepal width'], label='setosa')
    plt.scatter(df[50:100]['sepal length'], df[50:100]['sepal width'], label='virginica')
    plt.xlabel('sepal length')
    plt.ylabel('sepal width')
    plt.legend()
    plt.show()
    
    return df

# 2. 自编程实现感知机（随机梯度下降）
def manual_perceptron_implementation():
    """手动实现感知机算法"""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['label'] = iris.target
    df.columns = ['sepal length', 'sepal width', 'petal length', 'petal width', 'label']
    
    # 选取前100行（setosa和virginica两类）
    data = np.array(df.iloc[:100, [0, 1, -1]])
    X, y = data[:, :-1], data[:, -1]
    
    # 将标签转换为+1/-1
    for i in range(len(data)):
        if data[i, -1] == 0:
            data[i, -1] = -1
    
    # 感知机核心算法
    def check(data, w, b, X_train, y_train):
        for i in range(len(X_train)):
            if y_train[i] * (np.dot(X_train[i], w) + b) <= 0:
                return False
        return True
    
    def fit(data, X_train, y_train):
        w = np.ones(len(data[0]) - 1, dtype=np.float32)
        b = 0
        l_rate = 0.1
        while not check(data, w, b, X_train, y_train):
            for i in range(len(X_train)):
                if y_train[i] * (np.dot(X_train[i], w) + b) <= 0:
                    w += l_rate * y_train[i] * X_train[i]
                    b += l_rate * y_train[i]
        return w, b
    
    w, b = fit(data, X, y)
    print(f"手动实现感知机权重: {w}")
    print(f"手动实现感知机偏置: {b}")
    
    # 绘制分类线
    x_points = np.linspace(4, 7, 10)
    y_ = -(w[0] * x_points + b) / w[1]
    plt.plot(x_points, y_)
    plt.plot(data[:50, 0], data[:50, 1], 'bo', color='blue', label='setosa')
    plt.plot(data[50:100, 0], data[50:100, 1], 'bo', color='orange', label='virginica')
    plt.xlabel('sepal length')
    plt.ylabel('sepal width')
    plt.legend()
    plt.show()
    
    return w, b

# 3. 使用Sklearn库实现感知机
def sklearn_perceptron_implementation():
    """使用Sklearn库实现感知机"""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['label'] = iris.target
    df.columns = ['sepal length', 'sepal width', 'petal length', 'petal width', 'label']
    
    # 选取前100行（setosa和virginica两类）
    data = np.array(df.iloc[:100, [0, 1, -1]])
    
    # 将标签转换为+1/-1
    for i in range(len(data)):
        if data[i, -1] == 0:
            data[i, -1] = -1
    
    X, y = data[:, :-1], data[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # 定义感知机模型
    clf = Perceptron(fit_intercept=False, max_iter=1000, shuffle=False)
    clf.fit(X_train, y_train)
    
    print(f"Sklearn感知机权重: {clf.coef_}")
    print(f"Sklearn感知机偏置: {clf.intercept_}")
    print(f"迭代次数: {clf.n_iter_}")
    print(f"训练集准确率: {clf.score(X_train, y_train)*100:.2f}%")
    print(f"测试集准确率: {clf.score(X_test, y_test)*100:.2f}%")
    
    # 绘制分类线
    x_points = np.arange(4, 8)
    y_ = -(clf.coef_[0][0] * x_points + clf.intercept_) / clf.coef_[0][1]
    plt.plot(x_points, y_, 'r', label='sklearn Perceptron分类线')
    plt.plot(data[:50, 0], data[:50, 1], 'bo', color='blue', label='setosa')
    plt.plot(data[50:100, 0], data[50:100, 1], 'bo', color='orange', label='virginica')
    plt.xlabel('sepal length(cm)')
    plt.ylabel('sepal width(cm)')
    plt.title('Iris Perceptron classifier', fontsize=15)
    plt.legend()
    plt.show()
    
    return clf

# 4. 思考题答案
def print_answers_to_questions():
    """打印思考题答案"""
    print("\n" + "="*50)
    print("思考题答案")
    print("="*50)
    
    print("\n1、在做数据处理时，为什么要转化为dataFrame格式来处理，不能直接用numpy吗？")
    print("""
    答：
    1. DataFrame的列名便于理解和访问特定特征
    2. DataFrame可以同时存储不同类型的数据（数值、字符串等），而numpy数组通常要求统一数据类型
    3. DataFrame提供了describe()、head()、tail()等方法便于快速查看数据特征，数据探索更方便
    """)
    
    print("\n2、怎样挑选合适的特征来做分类，理由是什么？")
    print("""
    答：
    1. 通过可视化不同特征组合的散点图来观察特征间的相关性，选择最接近线性可分的一组特征。
       从散点图可以看出，sepal length和sepal width这两个特征能够较好地区分两类鸢尾花
    2. 通过PCA降维，选择解释方差比最高的两个特征。
       PCA分析显示前两个主成分已经解释了97%以上的方差，说明这两个特征包含了大部分信息。
    """)
    
    print("\n3、为什么要使用随机种子做数据分割？")
    print("""
    答：
    为了确保实验的可重复性，在模型调试和参数调优过程中，固定数据分割可以排除数据随机性带来的影响，
    专注于模型本身的改进。
    """)
    
    print("\n4、使用sklearn库来编码，学习率对迭代过程和最终结果有无影响？若有/无影响的话，条件是什么？")
    print("""
    答：
    有影响，影响条件：
    1. 当数据线性可分时，学习率主要影响收敛速度，不影响最终结果；
    2. 当数据不是完全线性可分时：学习率会影响最终结果，过大的学习率可能导致震荡，
       过小的学习率可能导致收敛过慢或陷入局部最优。
    """)

if __name__ == "__main__":
    print("实验二：感知机模型与鸢尾花分类")
    print("作者: 【NAME】")
    print("学号: 【ID】")
    print("="*50)
    
    # 执行各个部分
    df = prepare_and_visualize_data()
    w, b = manual_perceptron_implementation()
    clf = sklearn_perceptron_implementation()
    print_answers_to_questions()
