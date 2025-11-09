# -*- coding: utf-8 -*-
"""
本模块功能：证券指标趋势分析，多点标记图，动态交互图，相关性分析
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年10月17日
最新修订日期：
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用！
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.security_trend2 import *
from siat.grafix2 import *

#==============================================================================
import pandas as pd
import numpy as np

import datetime as dt; todaydt=str(dt.date.today())
#==============================================================================
#==============================================================================
if __name__=='__main__':
    #测试组1
    ticker='JD'
    indicator='Exp Ret%'
    start='2022-1-1'
    end='2022-12-31'
    
    df=security_trend(ticker,indicator=indicator)
    
    #测试组2
    ticker='AAPL'
    indicator=['Close','Open']
    start='default'
    end='default'
    loc='upper left'
    
    #测试组3
    ticker='AAPL'
    indicator=['Close','Open','High','Low']
    start='default'
    end='default'
    loc='upper left'
    
    #测试组4
    ticker=["GCZ25.CMX","GCZ24.CMX"]
    indicator='Close'
    start="2020-1-1"
    end="2020-6-30"
    
    #测试组5
    ticker=["180801.SZ","180101.SZ"]
    indicator='Close'
    start="2024-1-1"
    end="2024-5-30"   
    ticker_type='fund'
    
    #测试组6
    ticker="851242.SW"
    ticker='807110.SW'
    indicator='Close'; adjust=''
    start="2024-1-1"
    end="2024-9-30"
    ticker_type='auto'  
    
    #测试组6
    ticker='301161.SZ'
    indicator='sharpe'
    start="2024-1-1"
    end="2024-9-30"
    
    rank_high=5; rank_low=5
    ret_type='Annual Adj Ret%'; RF=0; regression_period=365; market_index="auto"
    loc='best'
    preprocess='none'; scaling_option='change%'
    printout=True; source='auto'
    ticker_type='auto'
    facecolor='papayawhip'; canvascolor='whitesmoke'
    downsample=False
    method='argrel'
    
    df=security_trend(ticker,indicator,start,end,ticker_type=ticker_type)
    
    
def security_trend_peaktrough(ticker,indicator='Close', 
                   start='default',end='today', 
                   #标记点数
                   rank_high=5, rank_low=5, 
                       
                   # 关注值
                   attention_value=0,
                   
                   #波峰和波谷搜索方法
                   method='argrel', 
                   
                   #计算RAR和贝塔系数的基础参数    
                   ret_type='Annual Adj Ret%',RF=0,regression_period=365,market_index="auto", 

                   #数据预处理：本指令不适用
                   #preprocess='none',scaling_option='change%', 
                                                  
                   #降采样开关，适用于样本数多于300时
                   downsample=False,
                       
                   loc='best', 
                       
                   printout=False,source='auto', 
                   ticker_type='auto', 
                   facecolor='papayawhip',canvascolor='whitesmoke'):

    """
    ===========================================================================
    功能：组合指令，多点标记一个证券指标走势。
    主要参数：
    ticker：证券代码，支持多个经济体的证券，包括股票、基金、部分欧美衍生品。
    股票：单一股票，股票列表，支持全球主要证券市场的股票。
    债券：因数据来源关系，本指令暂不支持债券，计划首先支持最活跃的沪深可转债。
    基金：因数据来源关系，仅支持下列市场的部分基金：
    沪深交易所(ETF/LOF/REIT基金)，美市(ETF/REIT/共同基金)，日韩欧洲(部分ETF/REIT基金)。
    利率产品：因数据来源关系，仅支持欧美市场的部分利率产品。
    衍生品：因数据来源关系，仅支持欧美市场的部分商品、金融期货和期权产品（如股票期权）。
    投资组合：使用字典表示法，成分股仅支持全球交易所上市的主要股票（限同币种）。
    投资组合仅支持RAR指标和CAPM贝塔系数，其他指标暂不支持。
    
    indicator：支持证券价格、收益率、风险指标、估值指标、RAR指标和CAPM贝塔系数。
    证券价格：支持开盘价、收盘价、最高最低价。
    收益率：支持基本的日收益率、滚动收益率和扩展收益率。滚动收益率支持周、月、季度和年。
    风险指标：支持滚动收益率和扩展收益率的标准差（波动风险）和下偏标准差（损失风险）。
    RAR指标：支持夏普比率、詹森阿尔法、索替诺比率和特雷诺比率。
    估值指标：支持市盈率、市净率和市值。仅支持中国内地、中国香港、美股和波兰上市的股票。
    市值指标不支持市场指数。
    
    start：指定分析的开始日期或期间。日期格式：YYYY-mm-dd
    作为期间时，支持最近的1个月、1个季度、半年、1年、2年、3年、5年、8年、10年或今年以来。
    省略时默认为最近的1个月。
    end：指定分析的结束日期。日期格式：YYYY-mm-dd。省略时默认为今日。
    
    rank_high：标记的高拐点数目，默认5
    rank_low：标记的低拐点数目，默认5
    
    method：搜索拐点的方法，默认'argrel'方法，还可选'find_peaks'方法，或者两者综合'hybrid'
    
    ret_type、RF、regression_period和market_index：仅用于计算RAR指标和CAPM贝塔系数。
    ret_type：指定计算RAR的收益率类型，支持滚动和扩展收益率，不同种类的计算结果之间不可比。
    RF：指定年化无风险利率，非百分比数值。
    regression_period：指定CAPM回归时的日期期间跨度，为日历日（自然日），默认一年。
    market_index：用于计算CAPM回归贝塔系数时的市场收益率。
    系统能够自动识别全球主要证券市场的指数，其他证券市场可由人工指定具体的市场指数代码。
    
    graph：指定是否将分析结果绘制曲线，默认绘制。
    loc：用于指定绘图时图例的位置，包括左右上角（下角、中间）、上下中间或图中央。
    
    preprocess：绘图前是否进行数据预处理，默认不使用。
    预处理方式：支持标准化、正态化、取对数和同步缩放法，常用的为同步缩放法。
    scaling_option：指定同步缩放法的对齐选项，支持均值、最小值、起点值、百分比和变化率方法。
    其中，百分比和变化率方法常用。适用于数值差异大的价格走势对比分析，其他指标不适用或效果不明显。
    
    printout：仅适用于有相关功能的指标（例如RAR）打开结果表格输出，默认关闭。
    
    source：指定证券基础数据来源，默认由系统决定。当系统找到的数据不理想时，可手动指定。
    若指定雅虎财经数据源，需要拥有访问该网站的权限。
    
    """   
    # 仅支持一个证券和一个指标
    if isinstance(ticker,list):
        ticker=ticker[0]
    if isinstance(indicator,list):
        indicator=indicator[0]
    
    # 获取证券指标
    from siat.security_trend2 import security_trend
    df0=security_trend(ticker,indicator=indicator, \
                       start=start,end=end, \
                       
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
        print(f"  Sorry, no data found for {indicator} of {ticker} in the given period")
        return df0x
    if len(df0x) == 0:
        print(f"  Sorry, zero data found for {indicator} of {ticker} in the given period")
        return df0x
    
    # 降采样，也能起到一点平滑作用
    if downsample:
        #print("  Downsampling to avoid curve overcrowded ...")
        df=auto_downsample(df0x)
    else:
        df=df0x
    
    # 寻找局部极值点
    tp_indicator=indicator

    # 搜索局部拐点
    if method == 'argrel':
        # 通常效果较好
        print(f"  Searching turning points using {method} method ...")
        highs_df, lows_df=find_major_turning_points_gemini(df, tp_indicator)
        peaks=highs_df.head(rank_high)
        troughs=lows_df.head(rank_low)

    elif method == 'find_peaks':
        # 通常效果不佳
        print(f"  Searching turning points using {method} method ...")
        highs_df, lows_df=find_major_turning_points_copilot(df, tp_indicator)
        peaks=highs_df.head(rank_high)
        troughs=lows_df.head(rank_low)

    else:
        # 多数时候与argrel方法效果接近
        print(f"  Searching turning points using hybrid method ...")
        highs_df1, lows_df1=find_major_turning_points_gemini(df, tp_indicator)
        peaks1=highs_df1.head(rank_high)
        troughs1=lows_df1.head(rank_low)

        highs_df2, lows_df2=find_major_turning_points_copilot(df, tp_indicator)
        peaks2=highs_df2.head(rank_high)
        troughs2=lows_df2.head(rank_low)
        
        peaks = pd.concat([peaks1, peaks2], ignore_index=True)
        peaks.drop_duplicates(subset=['Date'], keep='first', inplace=True)
        
        troughs = pd.concat([troughs1, troughs2], ignore_index=True)
        troughs.drop_duplicates(subset=['Date'], keep='first', inplace=True)

    # 绘图    
    tp_ticker=ticker
    tp_ticker_name=ticker_name(tp_ticker)

    titletxt_cn=f"证券走势拐点分析：{tp_ticker_name}"
    titletxt_en=f"Security Trend Turning Points: {tp_ticker_name}"
    titletxt=text_lang(titletxt_cn,titletxt_en)
    
    ylabeltxt=ectranslate(tp_indicator)
    
    import datetime; todaydt=datetime.date.today().strftime("%Y-%m-%d")
    source_cn=f"综合数据来源：新浪财经/东方财富/Stooq/雅虎财经等"
    source_en=f"Data source: Sina/EM/Stooq/Yahoo"
    xlabeltxt=text_lang(f"{source_cn}，{todaydt}",f"{source_en}, {todaydt}")
    
    plot_turning_points(df, tp_indicator, peaks, troughs, 
                            rank_peak=rank_high,rank_trough=rank_low, 
                            attention_value=attention_value,
                            offset_pts=6, 
                            x_rotation=30, 
                            
                            titletxt=titletxt,xlabeltxt=xlabeltxt,ylabeltxt=ylabeltxt,
                            loc=loc,
                            
                            facecolor=facecolor,
                            canvascolor=canvascolor,
                            )

    
    return df

#==============================================================================
#==============================================================================
if __name__=='__main__':
    
    df=security_trend("000001.SS",start="MRY",graph=False)
    df=security_trend(["000001.SS"],start="MRY",graph=False)
        
    df=security_trend(["000001.SS","000300.SS"],start="MRY",graph=False)
    
    df=security_trend("600519.SS",indicator=["Close","Adj Close"],start="MRY",graph=False)

    ticker=["000001.SS","000300.SS"]
    indicator="Close"
    start='default'; end='default'
    width=1000; height=600
    title=None
    title_distance=0.95
    title_font=None
    
    
    
def security_trend_interactive(ticker,indicator='Close', 
                   start='default',end='today', 
                   
                   #关注值
                   attention_value=0,
                   
                   #计算RAR和贝塔系数的基础参数    
                   ret_type='Annual Adj Ret%',RF=0,regression_period=365,market_index="auto", 

                   #数据预处理    
                   #preprocess='none',scaling_option='change%', 
                                                  
                   #降采样开关，适用于样本数多于300时
                   downsample=False,
                       
                   loc='best', 
                       
                   printout=False,source='auto', 
                   ticker_type='auto', 
                   facecolor='papayawhip',canvascolor='whitesmoke'):

    """
    ===========================================================================
    功能：组合指令，标记多个证券指标点信息，支持多个证券、多个指标，动态多种绘图方式。
    主要参数：
    ticker：证券代码，支持多个经济体的证券，包括股票、基金、部分欧美衍生品。
    股票：单一股票，股票列表，支持全球主要证券市场的股票。
    债券：因数据来源关系，本指令暂不支持债券，计划首先支持最活跃的沪深可转债。
    基金：因数据来源关系，仅支持下列市场的部分基金：
    沪深交易所(ETF/LOF/REIT基金)，美市(ETF/REIT/共同基金)，日韩欧洲(部分ETF/REIT基金)。
    利率产品：因数据来源关系，仅支持欧美市场的部分利率产品。
    衍生品：因数据来源关系，仅支持欧美市场的部分商品、金融期货和期权产品（如股票期权）。
    投资组合：使用字典表示法，成分股仅支持全球交易所上市的主要股票（限同币种）。
    投资组合仅支持RAR指标和CAPM贝塔系数，其他指标暂不支持。
    
    indicator：支持证券价格、收益率、风险指标、估值指标、RAR指标和CAPM贝塔系数。
    证券价格：支持开盘价、收盘价、最高最低价。
    收益率：支持基本的日收益率、滚动收益率和扩展收益率。滚动收益率支持周、月、季度和年。
    风险指标：支持滚动收益率和扩展收益率的标准差（波动风险）和下偏标准差（损失风险）。
    RAR指标：支持夏普比率、詹森阿尔法、索替诺比率和特雷诺比率。
    估值指标：支持市盈率、市净率和市值。仅支持中国内地、中国香港、美股和波兰上市的股票。
    市值指标不支持市场指数。
    
    start：指定分析的开始日期或期间。日期格式：YYYY-mm-dd
    作为期间时，支持最近的1个月、1个季度、半年、1年、2年、3年、5年、8年、10年或今年以来。
    省略时默认为最近的1个月。
    end：指定分析的结束日期。日期格式：YYYY-mm-dd。省略时默认为今日。
    
    ret_type、RF、regression_period和market_index：仅用于计算RAR指标和CAPM贝塔系数。
    ret_type：指定计算RAR的收益率类型，支持滚动和扩展收益率，不同种类的计算结果之间不可比。
    RF：指定年化无风险利率，非百分比数值。
    regression_period：指定CAPM回归时的日期期间跨度，为日历日（自然日），默认一年。
    market_index：用于计算CAPM回归贝塔系数时的市场收益率。
    系统能够自动识别全球主要证券市场的指数，其他证券市场可由人工指定具体的市场指数代码。
    
    graph：指定是否将分析结果绘制曲线，默认绘制。
    loc：用于指定绘图时图例的位置，包括左右上角（下角、中间）、上下中间或图中央。
    
    preprocess：绘图前是否进行数据预处理，默认不使用。
    预处理方式：支持标准化、正态化、取对数和同步缩放法，常用的为同步缩放法。
    scaling_option：指定同步缩放法的对齐选项，支持均值、最小值、起点值、百分比和变化率方法。
    其中，百分比和变化率方法常用。适用于数值差异大的价格走势对比分析，其他指标不适用或效果不明显。
    
    printout：仅适用于有相关功能的指标（例如RAR）打开结果表格输出，默认关闭。
    
    source：指定证券基础数据来源，默认由系统决定。当系统找到的数据不理想时，可手动指定。
    若指定雅虎财经数据源，需要拥有访问该网站的权限。
    
    """   
    # 支持多个证券和一个指标，或一个证券的多个指标
    if isinstance(ticker,list) and len(ticker)==1:
        ticker=ticker[0]
        
    elif isinstance(indicator,list) and len(indicator)==1:
        indicator=indicator[0]
    
    elif isinstance(ticker,(str,dict)):
        if isinstance(indicator,str):
            model="T1I1"
        elif isinstance(indicator,list):
            model="T1IM"
        else:
            model="unknown"
        
    elif isinstance(ticker,list):
        if isinstance(indicator,str):
            model="TMI1"
        elif isinstance(indicator,list):
            model="TMI1"
        else:
            model="unknown"
            
    if model == "unknown":
        print(f"  Sorry, no idea on the combination of {ticker} and {indicator}")
        return None
    
    # 获取证券指标
    # 因嵌套调用，此处需要重新载入，否则可能无法找到函数
    from siat.security_trend2 import security_trend
    df0=security_trend(ticker,indicator=indicator, \
                       start=start,end=end, \
                       
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
        print(f"  Sorry, no data found for {indicator} of {ticker} in the given period")
        return df0x
    if len(df0x) == 0:
        print(f"  Sorry, zero data found for {indicator} of {ticker} in the given period")
        return df0x
    
    # 降采样，也能起到一点平滑作用
    if downsample:
        #print(f"  Downsampling to avoid curve overcrowded ...")
        df=auto_downsample(df0x)
    else:
        df=df0x

    # 绘图    
    if model in ["T1I1"]:
        title_key=ticker_name(ticker)
        ylabeltxt=ectranslate(indicator)
        colnames=indicator

    if model in ["T1IM"]:
        title_key=ticker_name(ticker)
        ylabeltxt=''
        colnames=indicator

    if model in ["TMI1"]:
        title_key=ectranslate(indicator)
        ylabeltxt=ectranslate(indicator)
        colnames=list(df)


    titletxt_cn=f"证券走势交互式分析：{title_key}"
    titletxt_en=f"Security Trend Interactive Analysis: {title_key}"
    titletxt=text_lang(titletxt_cn,titletxt_en)
    
    import datetime; todaydt=datetime.date.today().strftime("%y-%m-%d")
    source_cn=f"综合数据来源：新浪财经/东方财富/Stooq/雅虎财经等"
    source_en=f"Data source: Sina/EM/Stooq/Yahoo, "
    xlabeltxt=text_lang(f"{source_cn}，{todaydt}",f"{source_en}, {todaydt}")
    
    plot_dynamic_plotly(df, colnames, width=1000, height=600, 
                            attention_value=attention_value,
                            titletxt=titletxt,
                            #title_distance=0.95,
                            title_font=None,
                            xlabeltxt=xlabeltxt, ylabeltxt=ylabeltxt,
                            facecolor=facecolor,canvascolor=canvascolor,
                            )
    
    return df


#==============================================================================
if __name__=='__main__':
    ticker=["^SPX","000001.SS","^HSI"]
    indicator='Close'
    start='L2Y'; end='today'
    df=security_trend(ticker,start=start,end=end,graph=False)

    ret_type='Annual Adj Ret%'; RF=0; regression_period=365; market_index="auto" 
    
    method='pearson'
    window=252
    offset=None
    offset_range=5
    attention_value=None
    attention_point=None
    titletxt=None
    ylabeltxt=None
    xlabeltxt=None
      
    #降采样开关，适用于样本数多于300时
    downsample=False
    
    loc='best'
    
    printout=False; source='auto'; ticker_type='auto' 
    facecolor='papayawhip'; canvascolor='whitesmoke'


    
def security_trend_correlation(ticker,indicator='Close', 
            start='default',end='today', 
                               
            #计算RAR和贝塔系数的基础参数    
            ret_type='Annual Adj Ret%',RF=0,regression_period=365,market_index="auto", 
            
            method='pearson',
            window=252, #计算滚动相关性系数的窗口大小，越大越平滑
            
            offset=None,
            offset_range=None,
            best_offset_method='mean', #偏移天数最佳显著性筛选方法，支持median和mean，均值法更准确
            filter_method='none', #默认不滤波，强滤波可选hp_filter方法（Hodrick–Prescott 滤波）
            filter_window=10, #滤波窗口大小，仅供mean/median/rolling_regression滤波方法用
            filter_lamb=1600, #仅供hp_filter滤波方法用（默认 1600，季度数据常用）
            
            attention_value=None,
            attention_point=None,
              
            #降采样开关，适用于样本数多于300时
            downsample=False,
            
            loc='best', 
            
            printout=False,source='auto', 
            ticker_type='auto', 
            facecolor='papayawhip',canvascolor='whitesmoke'):

    """
    ===========================================================================
    功能：组合指令，标记多个证券指标点信息，支持多个证券、多个指标，动态多种绘图方式。
    主要参数：
    ticker：证券代码，支持多个经济体的证券，包括股票、基金、部分欧美衍生品。
    股票：单一股票，股票列表，支持全球主要证券市场的股票。
    债券：因数据来源关系，本指令暂不支持债券，计划首先支持最活跃的沪深可转债。
    基金：因数据来源关系，仅支持下列市场的部分基金：
    沪深交易所(ETF/LOF/REIT基金)，美市(ETF/REIT/共同基金)，日韩欧洲(部分ETF/REIT基金)。
    利率产品：因数据来源关系，仅支持欧美市场的部分利率产品。
    衍生品：因数据来源关系，仅支持欧美市场的部分商品、金融期货和期权产品（如股票期权）。
    投资组合：使用字典表示法，成分股仅支持全球交易所上市的主要股票（限同币种）。
    投资组合仅支持RAR指标和CAPM贝塔系数，其他指标暂不支持。
    
    indicator：支持证券价格、收益率、风险指标、估值指标、RAR指标和CAPM贝塔系数。
    证券价格：支持开盘价、收盘价、最高最低价。
    收益率：支持基本的日收益率、滚动收益率和扩展收益率。滚动收益率支持周、月、季度和年。
    风险指标：支持滚动收益率和扩展收益率的标准差（波动风险）和下偏标准差（损失风险）。
    RAR指标：支持夏普比率、詹森阿尔法、索替诺比率和特雷诺比率。
    估值指标：支持市盈率、市净率和市值。仅支持中国内地、中国香港、美股和波兰上市的股票。
    市值指标不支持市场指数。
    
    start：指定分析的开始日期或期间。日期格式：YYYY-mm-dd
    作为期间时，支持最近的1个月、1个季度、半年、1年、2年、3年、5年、8年、10年或今年以来。
    省略时默认为最近的1个月。
    end：指定分析的结束日期。日期格式：YYYY-mm-dd。省略时默认为今日。
    
    ret_type、RF、regression_period和market_index：仅用于计算RAR指标和CAPM贝塔系数。
    ret_type：指定计算RAR的收益率类型，支持滚动和扩展收益率，不同种类的计算结果之间不可比。
    RF：指定年化无风险利率，非百分比数值。
    regression_period：指定CAPM回归时的日期期间跨度，为日历日（自然日），默认一年。
    market_index：用于计算CAPM回归贝塔系数时的市场收益率。
    系统能够自动识别全球主要证券市场的指数，其他证券市场可由人工指定具体的市场指数代码。
    
    graph：指定是否将分析结果绘制曲线，默认绘制。
    loc：用于指定绘图时图例的位置，包括左右上角（下角、中间）、上下中间或图中央。
    
    printout：仅适用于有相关功能的指标（例如RAR）打开结果表格输出，默认关闭。
    
    source：指定证券基础数据来源，默认由系统决定。当系统找到的数据不理想时，可手动指定。
    若指定雅虎财经数据源，需要拥有访问该网站的权限。
    
    """ 
    DEBUG=False
    
    # 至少需要两个证券和一个指标
    if isinstance(ticker,str):
        print(f"  Sorry, I have only 1 ticker {ticker}, but I need at least 2 to calculate correlation")
        return None
    
    if isinstance(ticker,list) and len(ticker)==1:
        print(f"  Sorry, I have only 1 ticker {ticker[0]}, but I need at least 2 to calculate correlation")
        return None
        
    #仅支持一个指标
    if isinstance(indicator,list):
        indicator=indicator[0]
    
    #前推开始日期，留出第1个滚动窗口期间
    start,end=start_end_preprocess(start,end)
    start1=date_adjust(start,adjust=-int((window/252)*365+30))
    
    # 获取证券指标
    # 因嵌套调用，此处需要重新载入，否则可能无法找到函数
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
        print(f"  Sorry, no data found for {indicator} of {ticker} in the given period")
        return df0x
    if len(df0x) == 0:
        print(f"  Sorry, zero data found for {indicator} of {ticker} in the given period")
        return df0x
    
    # 降采样，也能起到一点平滑作用
    if downsample:
        #print(f"  Downsampling to avoid curve overcrowded ...")
        df=auto_downsample(df0x)
    else:
        df=df0x

    #将df的列名顺序与ticker保持一致
    tname=ticker_name(ticker)
    #找出tname中不在df中的字段
    tmissing = [col for col in tname if col not in df.columns]
    if len(tmissing) > 0:
        print(f"  #Warning: failed to get info for {tmissing}, try later")
    #找出tname和df共有的字段    
    tcommon = [col for col in tname if col in df.columns]
    df=df[tcommon]
    
    # 绘图   
    t1name=ticker_name(ticker[0])
    titletxt_cn=f"证券走势相关性分析：{t1name}"
    titletxt_en=f"Security Correlation Trend: {t1name}"
    titletxt=text_lang(titletxt_cn,titletxt_en)
    
    method=method.lower()
    if method == 'pearson':
        method_txt=text_lang("基于皮尔逊相关系数","Pearson coef")
        ylabeltxt=text_lang("皮尔逊相关系数","Pearson coef")
    if method == 'spearman':
        method_txt=text_lang("基于斯皮尔曼相关系数","Spearman coef")
        ylabeltxt=text_lang("斯皮尔曼相关系数","Spearman coef")

    window_txt=text_lang(f"相关性移动窗口为{window}个交易日",f"moving window {window} t-days")

    ft0=text_lang("【注】","[Note] ")
    ft1=text_lang(f"分析期间：{start}至{end}",f"Period: {start} to {end}")
    ft2=f"{method_txt}, {window_txt}"
    
    ft3_cn=f"证券(n)标记：n为正(负)数表示，期间内滞后(提前)n个交易日与标题证券整体上相关性最强"
    ft3_en=f"Security(n): +n (lag), -n (lead); corr vs title security = strongest at n t-days"
    ft3=text_lang(ft3_cn,ft3_en)
    
    ft4_cn=f"曲线线宽：线段越宽(窄)表示与标题证券的相关性越显著(越不显著)，最细处通常表示不相关"
    ft4_en=f"Line width: Wider (narrower) = more (less) significant corr with title security"
    ft4=text_lang(ft4_cn,ft4_en)
    
    if best_offset_method == 'mean':
        best_offset_method_txt=text_lang('均值法','mean')
    elif best_offset_method == 'median':
        best_offset_method_txt=text_lang('中位数法','median')
        
    if filter_method == 'none':
        filter_method_txt=text_lang('未进行滤波','no filter employed')
    elif filter_method == 'mean':
        filter_method_txt=text_lang('均值滤波','mean method')
    elif filter_method == 'median':
        filter_method_txt=text_lang('中位数滤波','median method')
    elif filter_method == 'ewm':
        filter_method_txt=text_lang('近期优先加权平均滤波','exponential-weighted')
    elif filter_method == 'hp_filter':
        filter_method_txt=text_lang('Hodrick–Prescott滤波','Hodrick–Prescott')
    elif filter_method == 'kalman':
        filter_method_txt=text_lang('卡尔曼滤波','Kalman')
    else:
        filter_method_txt=text_lang('未知滤波方法，未滤波','unknown method, no filter')
        
    ft5_cn=f"传导效应滞后(提前)天数评估方法：{best_offset_method_txt}，相关系数滤波方法：{filter_method_txt}"
    ft5_en=f"Conduction evaluation: {best_offset_method_txt}, correlation coefficient filter: {filter_method_txt}"
    ft5=text_lang(ft5_cn,ft5_en)
    
    import datetime; todaydt=datetime.date.today().strftime("%Y-%m-%d")
    source_cn=f"数据来源：综合新浪财经/东方财富/Stooq/雅虎财经等"
    source_en=f"Data source: Sina/EM/Stooq/Yahoo"
    ft9=text_lang(f"{source_cn}，{todaydt}",f"{source_en}, {todaydt}")
    
    xlabeltxt=ft0+ft1+', '+ft2+'\n'+ft3+'\n'+ft4+'\n'+ft5+'\n'+ft9
    
    #插值填补空值
    #tnames=ticker_name(ticker)
    #dfx=interpolate_df(df,tnames)
    df=interpolate_df(df)
    
    if DEBUG:
        print(f"=====DEBUG: df={df} before plot_trend_correlation")
    
    best_offset=plot_trend_correlation(
        df,
        method=method,
        window=window,
        offset=offset,
        offset_range=offset_range,
        best_offset_method=best_offset_method,
        filter_method=filter_method, #相关系数滤波方法
        filter_window=filter_window, #滤波窗口大小
        filter_lamb=filter_lamb, #HP filter        
        
        attention_value=attention_value,
        attention_point=attention_point,
        titletxt=titletxt,
        ylabeltxt=ylabeltxt,
        xlabeltxt=xlabeltxt,
        facecolor=facecolor,
        canvascolor=canvascolor,
        loc=loc,
        printout=printout,
    )
    
    return df

#==============================================================================
#==============================================================================











