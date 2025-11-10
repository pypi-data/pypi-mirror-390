# -*- coding: utf-8 -*-
"""
本模块功能：量化分析之证券价格高低趋势
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年9月16日
最新修订日期：2025年9月17日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')

from siat.common import *
from siat.translate import *
from siat.security_trend2 import *

#==============================================================================
import pandas as pd
import numpy as np

#==============================================================================
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300

plt.rcParams['figure.facecolor']='white' #背景颜色

plt.rcParams['axes.grid']=False

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    #设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}
    
    """
    if check_language() == "English":
        #设置英文字体
        plt.rcParams['font.sans-serif'] = ['Times New Roman']  # 设置默认字体
        mpfrc={'font.family': 'Times New Roman'}
    """
    
if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 

# 设置绘图风格字体大小
title_txt_size=16
ylabel_txt_size=12
xlabel_txt_size=12
legend_txt_size=12
annotate_size=11

if check_language() == "English":
    title_txt_size=20
    ylabel_txt_size=16
    xlabel_txt_size=16
    legend_txt_size=16
    annotate_size=13

#==============================================================================
#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'
    
    ticker='600519.SS'
    
    start='MRY'; end='today'
    window=252; price_type='Close'; facecolor='whitesmoke'

    #计算RAR和贝塔系数的基础参数    
    ret_type='Annual Adj Ret%'; RF=0; regression_period=365; market_index="auto", 
    
    ticker_type='auto'; source='auto',
    
    facecolor='whitesmoke',
    printout=False; graph=True,


def security_trend_highlow(ticker, 
                           indicator='Close', 
                           start='MRY', end='today', 
                                
                           window=21, 
                           
                   #计算RAR和贝塔系数的基础参数    
                   ret_type='Annual Adj Ret%',RF=0,regression_period=365,market_index="auto", 
                   
                   ticker_type='auto', source='auto',
                   
                   facecolor='whitesmoke',
                   printout=False,graph=True,

                   ):
    """
    功能：
        绘制证券价格曲线，辅之以最近windowge交易日内的最高最低收盘价曲线
        目的是评估当期价格是否已经接近区间内的最高或最低价
    
    参数：
        ticker：单个证券代码
        start：开始日期，默认'MRM'
        end：截至日期，默认'today'
        window：观察区间交易日天数，默认252个交易日（52周）
        indicator：证券价格类型，默认收盘价'Close', 可选前复权价'Adj Close'
        facecolor：背景颜色，默认灰白色'whitesmoke'
    """
    
    # 仅处理单个证券
    if isinstance(ticker,list):
        ticker=ticker[0]
    
    import matplotlib.dates as mdates
    
    # 延伸开始日期
    start,end=start_end_preprocess(start,end)    
    start1=date_adjust(start, adjust=-window *2)
    
    # 抓取证券价格
    """
    prices,found=get_price_1ticker(ticker,start1,end)
    if not (found == 'Found'):
        print(f"  #Warning: either {ticker} not found or no data available")
        return None
    """
    # 获取证券指标
    from siat.security_trend2 import security_trend
    df0=security_trend(ticker,indicator=indicator, \
                       start=start1,end=end, \
                       
                       #计算RAR和贝塔系数的基础参数    
                       ret_type=ret_type,RF=RF,regression_period=regression_period,market_index=market_index, \

                       #数据预处理    
                       #preprocess=preprocess,scaling_option=scaling_option, \
                           
                       printout=False,source=source, \
                       ticker_type=ticker_type,
                       graph=False)

    if isinstance(df0,(tuple,list)):
        df0x=df0[0]
    else:
        df0x=df0   
        
    if df0x is None:
        print(f"  Sorry, no info found for the {indicator} of {ticker}, check and try again")
        return None
        
    if len(df0x) == 0:
        print(f"  Sorry, empty info found for the {indicator} of {ticker} from {start} to {end}")
        return None
    
    # 检查价格类型
    collist=list(df0x.select_dtypes(include=['int', 'float']).columns)
    if len(collist) > 1:
        if not (indicator in collist):
            print(f"  #Warning: unsupported indicator {indicator}")
            print(f"  Supported indicator: {collist}")
            return None
    
        price1=df0x[[indicator]]
    else:
        price1=df0x
    
    # 真正的字段名
    col=list(price1)[0]
    # 计算 rolling high/low
    price1["High_Close"] = price1[col].rolling(window).max()
    price1["Low_Close"] = price1[col].rolling(window).min()
    
    # 截取区间数据
    df=price1[start:end]
    
    high_end=df["High_Close"].values[-1]
    low_end=df["Low_Close"].values[-1]
    close_end=df[col].values[-1]
    
    # 绘图
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 三条曲线（颜色 + 不同线型）
    ax.plot(df.index, df[col], color="black", linewidth=2.2, linestyle="-")       # 实线
    ax.plot(df.index, df["High_Close"], color="red", alpha=0.6, linewidth=1.2, linestyle="--")   # 虚线
    ax.plot(df.index, df["Low_Close"], color="blue", alpha=0.6, linewidth=1.2, linestyle="-.")   # 点划线
    
    # 填充区域：高-收盘（斜线 ///）
    ax.fill_between(
        df.index, df[col], df["High_Close"],
        where=(df["High_Close"] >= df[col]),
        color="red", alpha=0.1, hatch="///", edgecolor="red"
    )
    
    # 填充区域：低-收盘（点阵 ...）
    ax.fill_between(
        df.index, df[col], df["Low_Close"],
        where=(df["Low_Close"] <= df[col]),
        color="blue", alpha=0.1, hatch="...", edgecolor="blue"
    )
    
    # 在曲线末尾标注 + 箭头
    last_date = df.index[-1]
    
    ax.annotate(ectranslate(indicator)+f"({srounds(close_end)})", 
                xy=(last_date, df[col].iloc[-1]), 
                xytext=(25, 0), textcoords="offset points", 
                color="black", fontsize=annotate_size, fontweight="bold", va="center",
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2))
    
    ax.annotate(text_lang(f"{window}日最高点({srounds(high_end)})",f"{window} days highest({srounds(high_end)})"), 
                xy=(last_date, df["High_Close"].iloc[-1]), 
                xytext=(25, 12), textcoords="offset points",   # 往上偏移
                color="red", fontsize=annotate_size, va="bottom",
                arrowprops=dict(arrowstyle="->", color="red", lw=1, alpha=0.6))
    
    ax.annotate(text_lang(f"{window}日最低点({srounds(low_end)})",f"{window} days lowest({srounds(low_end)})"), 
                xy=(last_date, df["Low_Close"].iloc[-1]), 
                xytext=(25, -12), textcoords="offset points",  # 往下偏移
                color="blue", fontsize=annotate_size, va="top",
                arrowprops=dict(arrowstyle="->", color="blue", lw=1, alpha=0.6))
    
    # 横轴日期格式化为 "YYYY-MM"
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=30)
    
    tname=ticker_name(ticker)
    #titletxt_cn=f"证券价格高低点趋势分析：{ticker_name(ticker)}，近期{window}个(交易)日"
    titletxt_cn=f"证券指标高低点范围与趋势分析：{tname}"
    #titletxt_en=f"Security Price High-Low Trend: {ticker_name(ticker)}, Recent {window} (Trading) Days"
    titletxt_en=f"Security Indicator High-Low Range & Trend: {tname}"
    titletxt=text_lang(titletxt_cn,titletxt_en)
    
    lang=check_language()
    if lang == 'English':
        plt.title('\n'+titletxt+'\n',fontweight='bold',fontsize=title_txt_size - 2)
    else:
        plt.title('\n'+titletxt+'\n',fontweight='bold',fontsize=title_txt_size)
    
    import datetime; todaydt = datetime.date.today()
    sourcetxt=text_lang("注：基于交易日天数。数据来源：新浪/Stooq/雅虎","Note: based on trading days. Data source: Sina/Stooq/Yahoo")
    footnote=sourcetxt+', '+str(todaydt)
    plt.xlabel('\n'+footnote+'\n',fontsize=xlabel_txt_size,ha='center') #空一行，便于截图底行留白
    
    plt.ylabel(ectranslate(indicator),fontsize=ylabel_txt_size)
    
    plt.gca().set_facecolor(facecolor)
    
    plt.tight_layout()
    plt.show()
    plt.close()
    
    return df

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================


