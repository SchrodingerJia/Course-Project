import numpy as np
import pandas as pd
from pandas import Series, DataFrame

data = pd.read_excel('../data/beijing_air_quality.xlsx')
data = data.replace(0, np.NaN)
data['年'] = data['日期'].apply(lambda x: x.year)
month = data['日期'].apply(lambda x: x.month)
quarter_month = {'1': '一季度', '2': '一季度', '3': '一季度',
                 '4': '二季度', '5': '二季度', '6': '二季度',
                 '7': '三季度', '8': '三季度', '9': '三季度',
                 '10': '四季度', '11': '四季度', '12': '四季度'}
data['季度'] = month.map(lambda x: quarter_month[str(x)])
bins = [0, 50, 100, 150, 200, 300, 1000]
data['等级'] = pd.cut(data['AQI'], bins, labels=['一级优', '二级良', '三级轻度污染', '四级中度污染', '五级重度污染', '六级严重污染'])
print('对AQI的分组结果：\n{0}'.format(data[['日期', 'AQI', '等级', '季度']]))

from collections.abc import Iterable
print(isinstance(month, Iterable))

print('各季度AQI和PM2.5的均值:\n{0}'.format(data.loc[:, ['AQI', 'PM2.5']].groupby(data['季度']).mean()))
print('各季度AQI和PM2.5的描述统计量:\n', data.groupby(data['季度'])['AQI', 'PM2.5'].apply(lambda x: x.describe()))

def top(df, n=10, column='AQI'):
    return df.sort_values(by=column, ascending=False)[:n]

print('空气质量最差的5天:\n', top(data, n=5)[['日期', 'AQI', 'PM2.5', '等级']])
print('各季度空气质量最差的3天:\n', data.groupby(data['季度']).apply(lambda x: top(x, n=3)[['日期', 'AQI', 'PM2.5', '等级']]))
print('各季度空气质量情况:\n', pd.crosstab(data['等级'], data['季度'], margins=True, margins_name='总计', normalize=False))

print(pd.get_dummies(data['等级']))
print(data.join(pd.get_dummies(data['等级'])))

np.random.seed(123)
sampler = np.random.randint(0, len(data), 10)
print(sampler)
sampler = np.random.permutation(len(data))[:10]
print(sampler)
print(data.take(sampler))
print(data.loc[data['质量等级'] == '优', :])