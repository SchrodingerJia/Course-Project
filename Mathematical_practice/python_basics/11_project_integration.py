import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于显示中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 数据导入
filepath = '.\\'
iris = pd.read_csv(filepath + 'iris.csv', index_col=0)  # 第一列作为索引
# 查看前几行数据
print(iris.head())
# 查看数据结构
print(iris.info())
## 数据的描述统计
print(iris.describe())
## 绘制箱型图
plt.figure(figsize=(12, 6))
sns.boxplot(data=iris.drop(columns='Species'))
plt.title('所有物种的箱形图')
plt.tight_layout()
plt.show()
## 查看分位数
print(iris.select_dtypes(include=['float64', 'int64']).quantile([0.1, 0.9]))
## 绘制散点图
plt.figure(figsize=(10, 6))
colors = {'setosa': 'blue', 'versicolor': 'green', 'virginica': 'red'}
for species, group in iris.groupby('Species'):
    plt.scatter(group['Petal.Width'], group['Petal.Length'], 
                label=species, c=colors[species], alpha=0.7)
plt.title('花瓣宽度与长度的关系')
plt.xlabel('花瓣宽度 (Petal Width)')
plt.ylabel('花瓣长度 (Petal Length)')
plt.legend(title='鸢尾花种类')
plt.grid(True)
plt.show()
## 绘制直方图
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.histplot(data=iris, x='Petal.Width', kde=True, bins=15, color='skyblue')
plt.title('所有物种的花瓣宽度分布')
plt.subplot(1, 2, 2)
sns.histplot(data=iris, x='Petal.Width', hue='Species', kde=True, 
             element='step', bins=15, palette=list(colors.values()))
plt.title('按物种分类的花瓣宽度分布')
plt.tight_layout()
plt.show()