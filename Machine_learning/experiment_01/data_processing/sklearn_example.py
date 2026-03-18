import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split

#加载数据
iris = load_iris()
# 将鸢尾花4个特征，以4列存入pandas的数据框架
df = pd.DataFrame(iris.data, columns=iris.feature_names)
# 在最后一列追加 加入（目标值）列数据
df['label'] = iris.target
# 选取数据，前100行，前两个特征，最后一列的目标值
data = np.array(df.iloc[:100, [0, 1, -1]])
# 生成感知机的标签值，+1， -1, 第一种 - 1，第二种 + 1
for i in range(len(data)):
    if data[i,-1] == 0:
        data[i,-1] = -1
#数据分割
# X是除最后一列外的所有列，y是最后一列
X, y = data[:, :-1], data[:, -1]
# 调用sklearn的train_test_split方法，将数据随机分为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X,  #被划分的样本特征集
                                                    y,  #被划分的样本目标集
                                                    test_size=0.3, #测试样本占比
                                                    random_state=1) #随机数种子
# 定义感知机
clf = Perceptron(fit_intercept=False, max_iter=1000, shuffle=False)
# 使用训练数据进行训练
clf.fit(X_train, y_train)
#评价模型
print(clf.score(X_test, y_test))