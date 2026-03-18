import pandas as pd
# 作业1: 学生成绩数据的处理和基本分析
 
 
## 成绩读取
 
 
df1 = pd.read_csv('../data/report_card_1.txt', sep='\t')
df2 = pd.read_csv('../data/report_card_2.txt', sep='\t')
df2 = pd.read_csv('ReportCard2.txt', sep='\t')
 
 
print(df1.head(5))
print(df2.head(5))
 
 
## 数据合并
 
 
df = pd.merge(df1, df2, on='id', how='outer')
 
 
print(len(df))
print(df.head(5))
 
 
## 处理缺失值
 
 
# 使用0值代替Nan
df_ = df.fillna({'politics':0})
 
 
print(df_.head(5))
 
 
## 数据验证
 
 
score_columns = [col for col in df.columns if col != 'id' and col != 'sex']
# 创建异常值表
outliers = pd.DataFrame()
for col in score_columns:
    outliers[f'{col}'] = ~df[col].between(0, 100)
 
 
print(outliers.head(5))
 
 
## 创建新特征
 
 
# 偏科指数
df['bias'] = df[score_columns].max(axis=1) - df[score_columns].min(axis=1)
 
 
print(df.head(5))
 
 
## 成绩标准化
 
 
standardized_df = df.copy()
for col in score_columns:
    mean = standardized_df[col].mean()
    std = standardized_df[col].std()
    standardized_df[col] = (standardized_df[col] - mean) / std
 
 
print(standardized_df.head(5))
 
 
## 成绩分布统计
 
 
distribution_stats = pd.DataFrame()
for col in score_columns:
    stats_dict = {
        '均值': df[col].mean(),
        '中位数': df[col].median(),
        '标准差': df[col].std(),
        '极差': df[col].max() - df[col].min(),
        '分四分位距': df[col].quantile(0.75) - df[col].quantile(0.25)
    }
    distribution_stats[col] = pd.Series(stats_dict)
 
 
print(df.head(5))
print(distribution_stats)
 
 
# 作业2: 学生成绩数据的图形化展示
 
 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import parallel_coordinates
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
 
 
# 绘制各科目成绩的箱线图
 
 
plt.figure(figsize=(8, 6))
box_plot = sns.boxplot(data=df[score_columns])
plt.title('各科目成绩箱线图')
plt.tight_layout()
plt.show()
 
 
## 创建相关性热力图
 
 
plt.figure(figsize=(10, 8))
correlation_matrix = df[score_columns].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('各科目成绩相关性热力图')
plt.tight_layout()
plt.show()
 
 
## 平行坐标图
 
 
# 计算平均成绩并划分等级
df['平均成绩'] = df[score_columns].mean(axis=1)
df['成绩等级'] = pd.cut(df['平均成绩'],
                       bins=[0, 60, 70, 80, 90, 100],
                       labels=['不及格', '及格', '中', '良', '优'])
# 准备平行坐标图数据
parallel_data = df[['成绩等级'] + score_columns].copy()
parallel_data['成绩等级'] = parallel_data['成绩等级'].astype('category')
plt.figure(figsize=(12, 6))
parallel_coordinates(parallel_data, '成绩等级',
                    colormap='viridis',
                    alpha=0.5)
plt.title('不同成绩群体的平行坐标图')
plt.xticks(rotation=45)
plt.legend(title='成绩等级', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
 
 
## 绘制男女生各科目成绩对比的雷达图
 
 
# 计算男女各科平均分
gender_avg = df.groupby('sex')[score_columns].mean()
# 设置雷达图参数
categories = score_columns
N = len(categories)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # 闭合图形
# 创建雷达图
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
# 绘制男生的雷达图
values = gender_avg.loc[1.0].tolist()
values += values[:1]  # 闭合图形
ax.plot(angles, values, 'o-', linewidth=2, label='男生')
ax.fill(angles, values, alpha=0.25)
# 绘制女生的雷达图
values = gender_avg.loc[2.0].tolist()
values += values[:1]  # 闭合图形
ax.plot(angles, values, 'o-', linewidth=2, label='女生')
ax.fill(angles, values, alpha=0.25)
# 设置雷达图属性
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.set_ylim(0, 100)
plt.title('男女生各科目成绩对比雷达图')
plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
plt.tight_layout()
plt.show()
 