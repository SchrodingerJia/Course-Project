import numpy as np
import pandas as pd
from pandas import Series, DataFrame

# Example 1: Series
print("Example 1: Series")
data = Series([1, 2, 3, 4, 5, 6, 7, 8, 9], index=['ID1', 'ID2', 'ID3', 'ID4', 'ID5', 'ID6', 'ID7', 'ID8', 'ID9'])
print('Values in the series:\n{0}'.format(data.values))
print('Index of the series:\n{0}'.format(data.index))
print('Access values at positions 0 and 2:\n{0}'.format(data[[0, 2]]))
print('Access values with index ID1 and ID3:\n{0}'.format(data[['ID1', 'ID3']]))
print('Check if ID1 exists: %s; Check if ID10 exists: %s' % ('ID1' in data, 'ID10' in data))

# Example 2: DataFrame from Excel
print("\nExample 2: DataFrame from Excel")
data = pd.read_excel('../data/beijing_air_quality.xlsx')
print('Type of data: {0}'.format(type(data)))
print('Row index of DataFrame: {0}'.format(data.index))
print('Column names of DataFrame: {0}'.format(data.columns))
print('Access all values of AQI and PM2.5:\n{0}'.format(data[['AQI', 'PM2.5']]))
print('Access AQI and PM2.5 for rows 2 to 3:\n{0}'.format(data.loc[1:2, ['AQI', 'PM2.5']]))
print('Access columns 2 and 4 for rows 1 to 2:\n{0}'.format(data.iloc[1:3, [1, 3]]))
data.info()

# Example 3: Data Merging and Handling Missing Values
print("\nExample 3: Data Merging and Handling Missing Values")
df1 = DataFrame({'key': ['a', 'd', 'c', 'a', 'b', 'd', 'c'], 'var1': range(7)})
df2 = DataFrame({'key': ['a', 'b', 'c', 'c'], 'var2': [0, 1, 2, 2]})
df = pd.merge(df1, df2, on='key', how='outer')
df.iloc[0, 2] = np.NaN
df.iloc[5, 1] = np.NaN
print('Merged data:\n{0}'.format(df))
df = df.drop_duplicates()
print('Data after removing duplicate rows:\n{0}'.format(df))
print('Check for missing values:\n{0}'.format(df.isnull()))
print('Check for non-missing values:\n{0}'.format(df.notnull()))
print('Data after dropping missing values:\n{0}'.format(df.dropna()))
fill_value = df[['var1', 'var2']].apply(lambda x: x.mean())
print('Fill missing values with mean:\n{0}'.format(df.fillna(fill_value)))