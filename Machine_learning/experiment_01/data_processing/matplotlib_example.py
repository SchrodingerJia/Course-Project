import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']  #解决中文显示乱码问题
plt.rcParams['axes.unicode_minus']=False

def plot_aqi_timeseries():
    """绘制AQI时间序列折线图"""
    data=pd.read_excel('../data/beijing_air_quality.xlsx')
    data=data.replace(0,np.NaN)
    plt.figure(figsize=(10,5))
    plt.plot(data['AQI'],color='black',linestyle='-',linewidth=0.5)
    plt.axhline(y=data['AQI'].mean(),color='red', linestyle='-',linewidth=0.5,label='AQI总平均值')
    data['年']=data['日期'].apply(lambda x:x.year)
    AQI_mean=data['AQI'].groupby(data['年']).mean().values
    year=['2014年','2015年','2016年','2017年','2018年','2019年']
    col=['red','blue','green','yellow','purple','brown']
    for i in range(6):
        plt.axhline(y=AQI_mean[i],color=col[i], linestyle='--',linewidth=0.5,label=year[i])
    plt.title('2014年至2019年AQI时间序列折线图')
    plt.xlabel('年份')
    plt.ylabel('AQI')
    plt.xlim(xmax=len(data), xmin=1)
    plt.ylim(ymax=data['AQI'].max(),ymin=1)
    plt.yticks([data['AQI'].mean()],['AQI平均值'])
    plt.xticks([1,365,365*2,365*3,365*4,365*5],['2014','2015','2016','2017','2018','2019'])
    plt.legend(loc='best')
    plt.text(x=list(data['AQI']).index(data['AQI'].max()),y=data['AQI'].max()-20,s='空气质量最差日',color='red')
    plt.show()

def plot_multiple_subplots():
    """绘制多子图"""
    import warnings
    warnings.filterwarnings(action = 'ignore')
    data=pd.read_excel('../data/beijing_air_quality.xlsx')
    data=data.replace(0,np.NaN)
    data['年']=data['日期'].apply(lambda x:x.year)
    AQI_mean=data['AQI'].groupby(data['年']).mean().values
    
    plt.figure(figsize=(10,5))
    plt.subplot(2,2,1)
    plt.plot(AQI_mean,color='black',linestyle='-',linewidth=0.5)
    plt.title('各年AQI均值折线图')
    plt.xticks([0,1,2,3,4,5,6],['2014','2015','2016','2017','2018','2019'])
    plt.subplot(2,2,2)
    plt.hist(data['AQI'],bins=20)
    plt.title('AQI直方图')
    plt.subplot(2,2,3)
    plt.scatter(data['PM2.5'],data['AQI'],s=0.5,c='green',marker='.')
    plt.title('PM2.5与AQI散点图')
    plt.xlabel('PM2.5')
    plt.ylabel('AQI')
    plt.subplot(2,2,4)
    tmp=pd.value_counts(data['质量等级'],sort=False)  #等同：tmp=data['质量等级'].value_counts()
    share=tmp/sum(tmp)
    labels=tmp.index
    explode = [0, 0.2, 0, 0, 0,0.2,0]
    plt.pie(share, explode = explode,labels = labels, autopct = '%3.1f%%',startangle = 180, shadow = True)
    plt.title('空气质量整体情况的饼图')
    plt.show()

def plot_optimized_subplots():
    """绘制优化调整后的多子图"""
    data=pd.read_excel('../data/beijing_air_quality.xlsx')
    data=data.replace(0,np.NaN)
    data['年']=data['日期'].apply(lambda x:x.year)
    AQI_mean=data['AQI'].groupby(data['年']).mean().values
    tmp=pd.value_counts(data['质量等级'],sort=False)
    share=tmp/sum(tmp)
    labels=tmp.index
    explode = [0, 0.2, 0, 0, 0,0.2,0]
    
    fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(10,5))
    axes[0,0].plot(AQI_mean,color='black',linestyle='-',linewidth=0.5)
    axes[0,0].set_title('各年AQI均值折线图')
    axes[0,0].set_xticks([0,1,2,3,4,5,6])
    axes[0,0].set_xticklabels(['2014','2015','2016','2017','2018','2019'])
    axes[0,1].hist(data['AQI'],bins=20)
    axes[0,1].set_title('AQI直方图')
    axes[1,0].scatter(data['PM2.5'],data['AQI'],s=0.5,c='green',marker='.')
    axes[1,0].set_title('PM2.5与AQI散点图')
    axes[1,0].set_xlabel('PM2.5')
    axes[1,0].set_ylabel('AQI')
    axes[1,1].pie(share, explode = explode,labels = labels, autopct = '%3.1f%%',startangle = 180, shadow = True)
    axes[1,1].set_title('空气质量整体情况的饼图')
    fig.subplots_adjust(hspace=0.5)
    fig.subplots_adjust(wspace=0.5)
    plt.show()

if __name__ == "__main__":
    plot_aqi_timeseries()
    plot_multiple_subplots()
    plot_optimized_subplots()