# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：Fama-French股票市场资产定价因子（中国大陆市场为估计值）
版本：2025-10-7，尚未测试，未加入allin.py
"""
#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.grafix import *

from siat.fama_french import *
#==============================================================================
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 

# 多种线型列表
linestyle_list=['-', #实线
                '--', #划线
                ':', #点线
                '-.', #点划线
                (0, (5, 2)), #自定义虚线
                (0, (1, 1)), #自定义点线
                (0, (10, 5, 2, 5)), #复杂点划线
            ]

color_list=['red','blue','green','orange','purple','cyan','black']
#==============================================================================
import pandas as pd
import numpy as np
#==============================================================================
def translate_scope_freq(scope,freq):
        
    # 翻译scope
    if scope in ['US']: scope_txt=text_lang("美国","U.S.")
    if scope in ['Global','GL']: scope_txt=text_lang("全球","Global")
    if scope in ['Europe','EU']: scope_txt=text_lang("欧洲","Europe")
    if scope in ['Japan','JP']: scope_txt=text_lang("日本","Japan")
    if scope in ['Asia_Pacific_ex_Japan','AP_ex_JP']: scope_txt=text_lang("亚太地区（不含日本）","Asia Pacific (ex Japan)")
    if scope in ['North_America','NA']: scope_txt=text_lang("北美地区","North America")
    if scope in ['Global_ex_US','GL_ex_US']: scope_txt=text_lang("全球（不含美国）","Global (ex US)")
    if scope in ['China','CN']: scope_txt=text_lang("中国","China")
    if scope in ['Emerging_Market','EM']: scope_txt=text_lang("新兴市场","Emerging Market")
    if scope in ['Developed_Market','DM']: scope_txt=text_lang("发达经济体","Developed Market")
    if scope in ['Developed_ex_US','DM_ex_US']: scope_txt=text_lang("发达经济体（除美国外）","Developed Market (ex US)")

    # 翻译freq
    if freq in ['daily']: freq_txt=text_lang("日频","daily")
    if freq in ['monthly']: freq_txt=text_lang("月度","monthly")
    if freq in ['yearly']: freq_txt=text_lang("年度","annual")

    return scope_txt,freq_txt
#==============================================================================
def fix_df_index(df0):
    """
    补全df索引中的残缺不全的日期，便于绘图
    """
    df=df0.copy()
    
    import pandas as pd
    
    # 新增：如果 index 是 PeriodIndex，则先转换为 Timestamp
    if isinstance(df.index, pd.PeriodIndex):
        df.index = df.index.to_timestamp()    

    # 将 index 转为字符串，便于处理
    df.index = df.index.astype(str)
    
    # 补全缺失部分：如果是 YYYY → 补成 YYYY-01-01；如果是 YYYY-MM → 补成 YYYY-MM-01
    def complete_date(s):
        parts = s.split('-')
        if len(parts) == 1:
            return f"{s}-01-01" #也可补全为f"{s}-06-30"
        elif len(parts) == 2:
            return f"{s}-01" #也可补全为f"{s}-15"
        else:
            return s  # 已是完整日期
    
    df.index = [complete_date(s) for s in df.index]
    
    # 转换为标准 datetime 格式
    df.index = pd.to_datetime(df.index, errors='coerce')  
    
    # 删除字段Date，避免后续程序计算时出错
    df.drop(columns=["Date"], errors='ignore', inplace=True)
    
    return df


if __name__=='__main__':
    start='2024-1-1'
    end='2024-12-31'
    scope='US'
    
    factor='FF3'
    factor='Mom'
    factor='FF5'
    
    freq='monthly'
    freq='daily'
    
    cols=['SMB']; TTM=True; loc='best'
    

#============================================================================== 
#============================================================================== 
#==============================================================================
if __name__=='__main__':
    start='2015-1-1'
    end='2024-12-31'
    scope='US'
    factor='FF3'
    
    freq='monthly'
    freq='daily'
    
    cols=None
    TTM=True
    annotate=True
    facecolor='whitesmoke'; loc='best'
    
    downsample=True
  
def plot_ff_factors(start, end, scope='US', factor='FF3', freq='monthly', \
                    cols=None,TTM=True,annotate=True, \
                        downsample=True, \
                        facecolor='whitesmoke',loc='best'):
    """
    绘制 Fama-French 因子走势
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scope (str): 国家或经济体, 如 'US', 'EU', 'JP', 'AP', 'GL', 'CN', 'HK'
        factor (str): 'FF3', 'FF5', 'Mom', 'ST_Rev', 'LT_Rev'
            'ST_Rev'和'LT_Rev'仅支持美国
        freq (str): 'daily', 'monthly', 'annual'
        cols (list): 要绘制的列名，例如 ['Mkt-RF','SMB','HML']
    """
    df9=pd.DataFrame()
    
    # 为滚动窗口前置252个交易日对应的日历日366日（多1日）
    if TTM:
        start1=date_adjust(start,adjust=-366)
    else:
        start1=start
    
    # 数据格式：因子值以百分数形式给出。在回归或计算时通常需要除以100转换为小数
    df0 = get_ff_factors(start1, end, scope=scope, factor=factor, freq=freq)
    if df0 is None:
        return None
    
    # 将索引中的日期标准化，补全日期！
    df=fix_df_index(df0)
    
    if factor in ['Mom','ST_Rev','LT_Rev']:
        cols=[factor]
    
    if cols is None:
        # 默认绘制除 RF 和 RF_annual 外的所有因子
        cols = [c for c in df.columns if c not in ['Date','RF','RF_annual']]

    _=plt.figure(figsize=(12.8,6.4))
    for c in cols:
        pos=cols.index(c)
        try:
            if TTM:
                if freq == 'daily':
                    df['c_smooth'] = df[c].rolling(window=252).mean()
                elif freq == 'monthly':
                    df['c_smooth'] = df[c].rolling(window=12).mean()
                else:
                    df['c_smooth'] = df[c].rolling(window=2).mean()
            else:
                df['c_smooth'] = df[c]

            df1=df.loc[start:end]
            c_mean=srounds(df1[c].mean())
            
            df9[c] = df1['c_smooth']
            
            label_txt=text_lang(f"{c} (均值{c_mean})",f"{c} (mean {c_mean})")
            
            # 降采样，稀疏化(sparse matrix)，避免绘制的折线过于密集，仅用于绘图
            dfsm=pd.DataFrame()
            if downsample:
                dfsm=auto_downsample(df1, col='c_smooth')
            else:
                dfsm['c_smooth']=df1['c_smooth']
                
            plt.plot(dfsm.index, dfsm['c_smooth'], label=label_txt,color=color_list[pos],ls=linestyle_list[pos])
            
            if annotate:
                # 添加文本标注
                x_last = dfsm.index[-1]
                y_last = dfsm['c_smooth'].iloc[-1]
                plt.text(x_last, y_last,
                         f" {c} {y_last:.2f}",
                         color=color_list[pos],
                         fontsize=10,
                         va='center', ha='left')             
            
        except:
            pass

    # 基准线
    plt.axhline(y=0, color='lightgray', linestyle=':', linewidth=2)
    
    scope_txt,freq_txt=translate_scope_freq(scope,freq)
    
    if TTM:
        title_cn=f"{factor}模型{freq_txt}因子TTM走势：{scope_txt}"
        title_en=f"{factor} Model {freq_txt.title()} Factor TTM Trend: {scope_txt}"
    else:
        title_cn=f"{factor}模型{freq_txt}因子走势：{scope_txt}"
        title_en=f"{factor} Model {freq_txt.title()} Factor Trend: {scope_txt}"
        
    plt.title(text_lang(title_cn,title_en)+'\n')
    
    import datetime; todaydt = datetime.date.today()
    ft_cn=f"数据来源：Fama/French Forum，"+str(todaydt)
    ft_en=f"Data source: Fama/French Forum, "+str(todaydt)
    plt.xlabel('\n'+text_lang(ft_cn,ft_en))  
    
    plt.ylabel(text_lang("模型因子（%）","Model Factor (%)"))
    plt.legend(loc=loc)
    
    plt.gca().set_facecolor(facecolor)
    #plt.grid(True)
    plt.show()
    
    return df9

if __name__=='__main__':
    # 绘制美国三因子月度走势
    plot_ff_factors('2024-01-01', '2024-12-31', scope='US', factor='FF3', freq='daily',cols=['SMB'])
    plot_ff_factors('2024-01-01', '2024-12-31', scope='US', factor='FF3', freq='monthly',cols=['SMB'])
    
    # 绘制美国四因子（自动拼接 FF3 + Momentum）
    plot_ff_factors('2020-01-01', '2023-12-31', scope='US', factor='Mom', freq='monthly')
    
    # 绘制欧洲五因子年度走势
    plot_ff_factors('2010-01-01', '2023-12-31', scope='Europe', factor='FF5', freq='yearly',cols=['SMB'])

#==============================================================================
if __name__=='__main__':
    start='2024-1-1'
    end='2024-12-31'
    
    scopes=['US','Europe']
    
    factor='FF3'
    factor='Mom'
    factor='FF5'
    
    freq='monthly'
    
    col='Mkt-RF'
    
def compare_ff_factors(start, end, scopes=['US','EU'], factor='FF3', freq='monthly', \
                       col='Mkt-RF',TTM=True,annotate=True, \
                           facecolor='whitesmoke',loc='best'):
    """
    对比多个国家/地区的 Fama-French 因子走势
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scopes (list): 国家或经济体列表, 如 ['US','EU','JP']
        factor (str): 'FF3', 'FF5', 'Mom', 'ST_Rev','LT_Rev'
            'ST_Rev'和'LT_Rev'仅支持美国
        freq (str): 'daily', 'monthly', 'annual'
        col (str): 要对比的因子列名，例如 'Mkt-RF', 'SMB', 'HML'
    """
    df9=pd.DataFrame()
    
    if factor in ['Mom','ST_Rev','LT_Rev']:
        # 这几个模型都只有一个因子
        col=factor    
    
    # 为滚动窗口前置252个交易日对应的日历日366日（多1日）
    if TTM:
        start1=date_adjust(start,adjust=-366)    
    else:
        start1=start
    
    _=plt.figure(figsize=(12.8,6.4))
    graf=False
    
    for scope in scopes:
        pos=scopes.index(scope)
        try:
            # 注意：因子数据为百分数
            df0 = get_ff_factors(start1, end, scope=scope, factor=factor, freq=freq)
            if df0 is None:
                print(f"  No combination found for {freq} {factor} in {scope} from {start} to {end}")
                continue
            if len(df0) == 0:
                print(f"  No data available for {freq} {factor} in {scope} from {start} to {end}")
                continue
            
            if col not in df0.columns:
                print(text_lang(f"  ... No {col} factor found in {scope} data, skip ...",f"  ... {scope} 数据中没有列 {col}，跳过 ..."))
                continue
            
            # 将索引中的日期标准化，补全日期！
            df=fix_df_index(df0)  

            graf=True
            
            if TTM:
                if freq == 'daily':
                    df['c_smooth'] = df[col].rolling(window=252).mean()
                elif freq == 'monthly':
                    df['c_smooth'] = df[col].rolling(window=12).mean()
                else:
                    df['c_smooth'] = df[col].rolling(window=2).mean()
            else:
                df['c_smooth'] = df[col]     
            
            df1=df.loc[start:end]  
            scope_mean=srounds(df1[col].mean())
            
            df9[scope]=df1['c_smooth']
            
            scope_txt,freq_txt=translate_scope_freq(scope,freq)  
            
            label_txt=text_lang(f"{scope_txt} (均值{scope_mean})",f"{scope_txt} (mean {scope_mean})")
            
            # 降采样，稀疏化(sparse matrix)，避免绘制的折线过于密集
            dfsm=pd.DataFrame()
            if downsample:
                dfsm=auto_downsample(df1, col='c_smooth')
            else:
                dfsm['c_smooth']=df1['c_smooth']          
            
            #plt.plot(df1.index, df1['c_smooth'], label=label_txt,color=color_list[pos],ls=linestyle_list[pos])
            plt.plot(dfsm.index, dfsm['c_smooth'], label=label_txt,color=color_list[pos],ls=linestyle_list[pos])
            
            if annotate:
                # 添加文本标注
                x_last = dfsm.index[-1]
                y_last = dfsm['c_smooth'].iloc[-1]
                plt.text(x_last, y_last,
                         f" {scope_txt} {y_last:.2f}",
                         color=color_list[pos],
                         fontsize=10,
                         va='center', ha='left')      
                
        except Exception as e:
            print(text_lang(f"  ... Failed in getting {scope} data: {e}",f"  ... 获取 {scope} 数据失败: {e}"))
    
    if graf:
        # 基准线
        plt.axhline(y=0, color='lightgray', linestyle=':', linewidth=2)

        if TTM:
            TTM_txt='TTM'
        else:
            TTM_txt=''

        if factor in ['Mom','ST_Rev','LT_Rev']:
            title_cn=f"{factor}模型{freq_txt}因子{TTM_txt}走势"
            if TTM_txt == '':
                title_en=f"{factor} Model {freq_txt.title()} Factor Trend"
            else:
                title_en=f"{factor} Model {freq_txt.title()} Factor {TTM_txt} Trend"
        else:
            title_cn=f"{factor}模型{freq_txt}因子{TTM_txt}走势：{col}"
            if TTM_txt == '':
                title_en=f"{factor} Model {freq_txt.title()} Factor Trend: {col}"
            else:
                title_en=f"{factor} Model {freq_txt.title()} Factor {TTM_txt} Trend: {col}"
            
        plt.title(text_lang(title_cn,title_en)+'\n')
        
        import datetime; todaydt = datetime.date.today()
        ft_cn=f"数据来源：Fama/French Forum，"+str(todaydt)
        ft_en=f"Data source: Fama/French Forum, "+str(todaydt)
        plt.xlabel('\n'+text_lang(ft_cn,ft_en))  
        
        plt.ylabel(text_lang("模型因子（%）","Model Factor (%)"))
        plt.legend(loc=loc)
        
        plt.gca().set_facecolor(facecolor)
        #plt.grid(True)
        plt.show()
    
    return df9



if __name__=='__main__':
    # 对比美国和欧洲的三因子模型中的市场因子 (Mkt-RF)
    compare_ff_factors('2015-01-01', '2023-12-31', scopes=['US','Europe'], \
                       factor='FF3', freq='monthly', col='Mkt-RF')
    
    # 对比美国、日本、全球的 SMB 因子
    compare_ff_factors('2010-01-01', '2023-12-31', scopes=['US','Japan','Global'], \
                       factor='FF3', freq='monthly', col='SMB')
    
    # 对比美国和欧洲的五因子模型中的盈利因子 (RMW)
    compare_ff_factors('2010-01-01', '2023-12-31', scopes=['US','Europe'], \
                       factor='FF5', freq='monthly', col='RMW')


#==============================================================================
import numpy as np

def compare_ff_cumulative(start, end, scopes=['US','EU'], factor='FF3', \
                          freq='monthly', col='Mkt-RF',annotate=True, \
                              downsample=True, \
                              facecolor='whitesmoke',loc='best'):
    """
    对比多个国家/地区的 Fama-French 因子累计收益走势
    
    📌 功能说明
    累计收益曲线：将因子收益率序列转为复利累计收益，起始点为 1。
    多国对比：支持多个国家/地区在同一张图中对比。
    灵活选择因子：支持 FF3、Mom、FF5 模型中的任意因子。
    频度支持：日度、月度、年度（自动转换）。
    错误处理：如果某个国家没有该因子，会自动跳过并提示。
    这样，就能展示不同国家因子长期表现的差异，例如“美国 vs 欧洲的市场风险溢价长期走势”。    
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scopes (list): 国家或经济体列表, 如 ['US','EU','JP']
        factor (str): 'FF3', 'FF5', 'Mom'
            'ST_Rev'和'LT_Rev'仅支持美国
        freq (str): 'daily', 'monthly', 'annual'
        col (str): 要对比的因子列名，例如 'Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'
    """
    df9=pd.DataFrame()
    
    if factor in ['Mom','ST_Rev','LT_Rev']:
        cols=factor 
        
    _=plt.figure(figsize=(12.8,6.4))
    
    for scope in scopes:
        scope_txt,freq_txt=translate_scope_freq(scope,freq)
        pos=scopes.index(scope)
        try:
            # 注意：获得的因子数据为百分数！
            df0 = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
            if df0 is None:
                print(f"  No combination found for {freq} {factor} in {scope} from {start} to {end}")
                continue
            if len(df0) == 0:
                print(f"  No data available for {freq} {factor} in {scope} from {start} to {end}")
                continue            
            
            if col not in df0.columns:
                print(text_lang(f"  ... {scope_txt}数据中没有列{col}，跳过 ...",f"  ... No {col} found in {scope_txt} columns, skip ..."))
                continue
            
            # 将索引中的日期标准化，补全日期！
            df=fix_df_index(df0)   
            df = df.drop(columns=['Date'], errors='ignore')
            
            # 将百分比收益率转为小数
            returns = df[col] / 100.0
            
            # 计算累计收益（复利）和复合增长率
            #cum_return = (1 + returns).cumprod()
            cum_return0 = (1 + returns).cumprod()
            dftmp = cum_return0.to_frame(name=scope)
            CAGR=cagr(dftmp,indicator=scope,printout=False)
            CAGR_pct=srounds(CAGR * 100)
            
            # 转化回百分数记录，用于绘图
            cum_return=(cum_return0 - 1) * 100
            # 转化回百分数记录，用于返回值，与其他函数的返回值保持一致
            df9[scope]=cum_return
            
            label_txt=text_lang(f"{scope_txt} (年化{CAGR_pct}%)",f"{scope_txt} ({CAGR_pct}% p.a.)")

            # 降采样，稀疏化(sparse matrix)，避免绘制的折线过于密集
            dfsm=pd.DataFrame()
            if downsample:
                dfsm=auto_downsample(df9, col=scope)
            else:
                dfsm[scope]=df9[scope]
            
            #plt.plot(df.index, cum_return, label=label_txt,color=color_list[pos],ls=linestyle_list[pos])
            plt.plot(dfsm.index, dfsm[scope], label=label_txt,color=color_list[pos],ls=linestyle_list[pos])
            
            if annotate:
                # 添加文本标注
                x_last = dfsm.index[-1]
                y_last = dfsm[scope].iloc[-1]
                plt.text(x_last, y_last,
                         f" {scope_txt} {y_last:.2f}%",
                         color=color_list[pos],
                         fontsize=10,
                         va='center', ha='left')             
            
        except Exception as e:
            print(text_lang(f"  ... 获取{scope_txt}数据失败: {e}","  ... Failed in getting {scope_txt} data: {e}"))
    
    # 基准线
    plt.axhline(y=0, color='lightgray', linestyle=':', linewidth=1)

    if factor in ['Mom','ST_Rev','LT_Rev']:
        title_cn=f"{factor}模型因子累计增长率走势"
        title_en=f"{factor} Model Factor Cumulative Growth Trend"
    else:
        title_cn=f"{factor}模型因子累计增长率走势：{col}"
        title_en=f"{factor} Model Factor Cumulative Growth Trend: {col}"
    plt.title(text_lang(title_cn,title_en)+'\n')
    
    import datetime; todaydt = datetime.date.today()
    ft_cn=f"注：使用{freq_txt}因子，数据来源：Fama/French Forum，"+str(todaydt)
    ft_en=f"Note: use {freq_txt} factors, data source: Fama/French Forum, "+str(todaydt)
    plt.xlabel('\n'+text_lang(ft_cn,ft_en))  
    
    #plt.ylabel(text_lang("累计收益率（基准=1）","Cumulative Return (Index=1)"))
    plt.ylabel(text_lang("模型因子的累计增长率（%）","Model Factor Cumulative Growth (%)"))
    plt.legend(loc=loc)
    
    plt.gca().set_facecolor(facecolor)
    #plt.grid(True)
    plt.show()

    
    return df9


if __name__=='__main__':
    # 对比美国和欧洲的市场因子累计收益
    compare_ff_cumulative('2010-01-01', '2023-12-31', scopes=['US','Europe'], factor='FF3', \
                          freq='monthly', col='Mkt-RF')
    
    # 对比美国、日本、全球的 SMB 因子累计收益
    compare_ff_cumulative('2010-01-01', '2023-12-31', scopes=['US','Japan','China'], \
                          factor='FF3', freq='monthly', col='SMB')
    
    # 对比美国和欧洲的盈利因子 (RMW) 累计收益
    compare_ff_cumulative('2010-01-01', '2023-12-31', scopes=['US','Europe'], \
                          factor='FF5', freq='monthly', col='RMW')

#==============================================================================
if __name__=='__main__':
    start='2010-01-01'; end='2023-12-31'
    scope='US'; factor='FF5'; freq='monthly',
    cols=['Mkt-RF','SMB','HML','RMW','CMA']
    
    
def compare_factors_cumulative_single_country(start, end, scope='US', factor='FF5', \
                                              freq='monthly', cols=None,annotate=True, \
                                                  downsample=True, \
                                                  facecolor='whitesmoke',loc='best'):
    """
    绘制单一国家/地区的多个 Fama-French 因子累计收益曲线
    
    📌 功能说明
    单国多因子对比：在同一张图中展示多个因子的累计收益曲线。
    灵活选择因子：支持 FF3、FF5 模型。
    自动处理频度：日度、月度、年度均可。
    默认绘制所有因子（除 RF 和 RF_annual），也可手动指定 cols。
    累计收益曲线：采用复利累计，起始点为 1。
    这样就能展示同一国家内部不同因子的长期表现差异，例如“美国市场因子中，SMB 与 HML 的长期走势对比”。    
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scope (str): 国家或经济体, 如 'US','EU','JP','AP','GL','CN','HK'
        factor (str): 'FF3', 'FF5', 'Mom'
            'ST_Rev'和'LT_Rev'仅支持美国
        freq (str): 'daily', 'monthly', 'annual'
        cols (list): 要绘制的因子列名，例如 ['Mkt-RF','SMB','HML','RMW','CMA']
    """
    df9=pd.DataFrame()
    
    # 注意：返回值为百分数
    df0 = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
    if df0 is None:
        print(f"  No combination found for {freq} {factor} in {scope} from {start} to {end}")
        return None
    if len(df0) == 0:
        print(f"  No data available for {freq} {factor} in {scope} from {start} to {end}")
        return None
    
    # 将索引中的日期标准化，补全日期！
    df=fix_df_index(df0)    

    if factor in ['Mom','ST_Rev','LT_Rev']:
        cols=[factor]
        
    if cols is None:
        # 默认绘制除 RF 和 RF_annual 外的所有因子
        cols = [c for c in df.columns if c not in ['Date','RF','RF_annual']]
    
    _=plt.figure(figsize=(12.8,6.4))
    
    for c in cols:
        pos=cols.index(c)
        if c not in df.columns:
            print(f"{scope} 数据中没有列 {c}，跳过。")
            continue
        
        returns = df[c] / 100.0
        #cum_return = (1 + returns).cumprod()
        cum_return0 = (1 + returns).cumprod()
        dftmp = cum_return0.to_frame(name=c)
        CAGR=cagr(dftmp,indicator=c,printout=False)
        CAGR_pct=srounds(CAGR * 100)
        
        cum_return = (cum_return0 - 1) * 100        
        
        df9[c]=cum_return
        
        label_txt=text_lang(f"{c} (年化{CAGR_pct}%)",f"{c} ({CAGR_pct}% p.a.)")
        
        # 降采样，稀疏化(sparse matrix)，避免绘制的折线过于密集
        dfsm=pd.DataFrame()
        if downsample:
            dfsm=auto_downsample(df9, col=c)
        else:
            dfsm[c]=df9[c] 
                
        #plt.plot(df.index, cum_return, label=label_txt,color=color_list[pos],ls=linestyle_list[pos])
        plt.plot(dfsm.index, dfsm[c], label=label_txt,color=color_list[pos],ls=linestyle_list[pos])
        
        if annotate:
            # 添加文本标注
            x_last = dfsm.index[-1]
            y_last = dfsm[c].iloc[-1]
            plt.text(x_last, y_last,
                     f" {c} {y_last:.2f}%",
                     color=color_list[pos],
                     fontsize=10,
                     va='center', ha='left')            
    
    # 基准线
    plt.axhline(y=0, color='lightgray', linestyle=':', linewidth=1)
    
    scope_txt,freq_txt=translate_scope_freq(scope,freq)
    
    title_cn=f"{factor}模型因子累计增长率走势：{scope_txt}"
    title_en=f"{factor} Model Factor Cumulative Growth Trend: {scope_txt}"
    plt.title(text_lang(title_cn,title_en)+'\n')
    
    import datetime; todaydt = datetime.date.today()
    ft_cn=f"注：使用{freq_txt}因子，数据来源：Fama/French Forum，"+str(todaydt)
    ft_en=f"Note: use {freq_txt} factors, data source: Fama/French Forum, "+str(todaydt)
    plt.xlabel('\n'+text_lang(ft_cn,ft_en))
    
    plt.ylabel(text_lang("模型因子累计增长率（%）","Model Factor Cumulative Growth (%)"))
    plt.legend(loc=loc)
    
    plt.gca().set_facecolor(facecolor)
    #plt.grid(True)
    plt.show()

    
    return df9

if __name__=='__main__':
    # 美国五因子模型：对比 Mkt-RF、SMB、HML、RMW、CMA
    compare_factors_cumulative_single_country(
        '2010-01-01', '2023-12-31',
        scope='US', factor='FF5', freq='monthly',
        cols=['Mkt-RF','SMB','HML','RMW','CMA']
    )
    
    # 欧洲三因子模型：对比 Mkt-RF、SMB、HML
    compare_factors_cumulative_single_country(
        '2010-01-01', '2023-12-31',
        scope='Europe', factor='FF3', freq='monthly'
    )
    
    # 日本四因子模型（FF3 + Momentum）
    compare_factors_cumulative_single_country(
        '2010-01-01', '2023-12-31',
        scope='Japan', factor='Mom', freq='monthly',
    )

    
#==============================================================================

def plot_ff_matrix(start, end, scopes=['US','EU','JP'], factor='FF5', \
                   freq='monthly', cols=None,facecolor='whitesmoke'):
    """
    绘制多国 × 多因子累计收益矩阵图

    矩阵布局：行 = 国家/地区，列 = 因子。
    累计收益曲线：采用复利累计，起始点为 1。
    灵活选择因子：默认绘制所有可用因子，也可通过 cols 指定。
    自动跳过缺失因子：如果某个国家没有该因子，子图会隐藏。
    适合教材展示：一张图就能展示跨国 × 多因子的长期表现差异。
    这样就能展示一个多维度对比图，例如“美国、欧洲、日本的五因子模型累计收益矩阵”，非常直观。
    
    参数:
        start (str): 开始日期, 格式 'YYYY-mm-dd'
        end (str): 结束日期, 格式 'YYYY-mm-dd'
        scopes (list): 国家或经济体列表, 如 ['US','EU','JP']
        factor (str): 'FF3', 'FF5', 'Mom'
        freq (str): 'daily', 'monthly', 'annual'
        cols (list): 要绘制的因子列名，例如 ['Mkt-RF','SMB','HML','RMW','CMA']
    """
    # 先获取第一个国家的数据，确定默认因子列
    df_sample = get_ff_factors(start, end, scope=scopes[0], factor=factor, freq=freq)
    if cols is None:
        cols = [c for c in df_sample.columns if c not in ['Date','RF','RF_annual']]
    
    n_rows = len(scopes)
    n_cols = len(cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows), sharex=True)
    
    if n_rows == 1: axes = [axes]  # 保证二维结构
    if n_cols == 1: axes = [[ax] for ax in axes]
    
    df_list=[]
    for i, scope in enumerate(scopes):
        try:
            df0 = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
            if df0 is None:
                print(f"  No combination found for {freq} {factor} in {scope} from {start} to {end}")
                continue
            if len(df0) == 0:
                print(f"  No data available for {freq} {factor} in {scope} from {start} to {end}")
                continue

            # 将索引中的日期标准化，补全日期！
            df=fix_df_index(df0)      
            df_list=df_list+[df]
            
            for j, c in enumerate(cols):
                ax = axes[i][j]
                if c not in df.columns:
                    ax.set_visible(False)
                    continue
                returns = df[c] / 100.0
                #cum_return = (1 + returns).cumprod()
                cum_return = (1 + returns).cumprod() - 1
                ax.plot(df.index, cum_return, label=f"{scope}:{c}")
                ax.set_title(f"{scope}:{c}")
                #ax.grid(True)
                if i == n_rows-1:
                    ax.set_xlabel("Date")
                if j == 0:
                    #ax.set_ylabel("Cumulative Growth (Benchmark=1)")
                    ax.set_ylabel("Cumulative Growth")
                    
                ax.set_facecolor(facecolor)
                
                ax.tick_params(axis='x', rotation=30)  # 设置 x 轴刻度旋转
        except Exception as e:
            print(f"获取 {scope} 数据失败: {e}")
    
    plt.tight_layout()
    plt.show()
    
    return df_list


if __name__=='__main__':
    # 美国、欧洲、日本的五因子模型，展示所有因子累计收益
    plot_ff_matrix(
        '2010-01-01', '2023-12-31',
        scopes=['US','Europe','Japan'],
        factor='FF5',
        freq='monthly'
    )
    
    # 美国、全球的三因子模型，只展示 Mkt-RF、SMB、HML
    plot_ff_matrix(
        '2010-01-01', '2023-12-31',
        scopes=['US','GL'],
        factor='FF3',
        freq='monthly',
        cols=['Mkt-RF','SMB','HML']
    )


#==============================================================================
if __name__=='__main__':
    # 一次性生成美国、欧洲、日本、全球的 FF3/FF5/Mom 月度累计收益图
    batch_generate_plots(
        start='2010-01-01',
        end='2023-12-31',
        scopes=['US','EU','JP','GL'],
        factors=['FF3','FF5','FFC4'],
        freqs=['monthly']
    )


import os

def save_ff_cumulative_plot(start, end, scope, factor, freq, cols=None, \
                            outdir="ff_plots"):
    """
    保存单国多因子累计收益图为 PNG 文件
    
    📌 功能亮点
    一键生成整套教材图表，省去手动绘制的麻烦。
    自动化：一行代码批量生成所有教材图表。
    可扩展：可以轻松增加 scopes、factors、freqs。
    高分辨率：保存为 300dpi PNG，适合教材/论文排版。
    健壮性：遇到缺失数据会跳过并提示，不会中断整个批处理。   
    
    运行后，会在当前目录下生成一个 ff_plots/ 文件夹，里面包含类似：
    ff_plots/
     ├── US_FF3_monthly.png
     ├── US_FF5_monthly.png
     ├── US_FFC4_monthly.png
     ├── EU_FF3_monthly.png
     ├── EU_FF5_monthly.png
     ├── EU_FFC4_monthly.png
     ├── JP_FF3_monthly.png
     ├── JP_FF5_monthly.png
     ├── JP_FFC4_monthly.png
     ├── GL_FF3_monthly.png
     ├── GL_FF5_monthly.png
     └── GL_FFC4_monthly.png
    
    
    
    """
    df0 = get_ff_factors(start, end, scope=scope, factor=factor, freq=freq)
    if df0 is None:
        print(f"  No combination found for {freq} {factor} in {scope} from {start} to {end}")
        return None
    if len(df0) == 0:
        print(f"  No data available for {freq} {factor} in {scope} from {start} to {end}")
        return None

    # 将索引中的日期标准化，补全日期！
    df=fix_df_index(df0)        
    
    if cols is None:
        cols = [c for c in df.columns if c not in ['Date','RF','RF_annual']]
    
    _=plt.figure(figsize=(12.8,6.4))
    for c in cols:
        if c not in df.columns:
            continue
        returns = df[c] / 100.0
        cum_return = (1 + returns).cumprod()
        plt.plot(df.index, cum_return, label=c)
    
    plt.title(f"{scope} {factor} 累计收益 ({freq})")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (Index=1)")
    plt.legend()
    #plt.grid(True)
    
    os.makedirs(outdir, exist_ok=True)
    fname = f"{outdir}/{scope}_{factor}_{freq}.png"
    plt.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"已保存图表: {fname}")


def batch_generate_plots(start, end, scopes=['US','EU','JP','GL'], factors=['FF3','FF5','FFC4'], freqs=['monthly']):
    """
    批量生成并保存教材图表
    """
    for scope in scopes:
        for factor in factors:
            for freq in freqs:
                try:
                    save_ff_cumulative_plot(start, end, scope, factor, freq)
                except Exception as e:
                    print(f"生成 {scope}-{factor}-{freq} 图表失败: {e}")

#==============================================================================
#==============================================================================

def security_trend_fffactor_1model(model='FF3',
                            indicator='SMB',
                            market='US',
                            start='L5Y',end='today',
                            frequency='monthly',
                            cumulative=True,
                            TTM=True,
                            annotate=True,
                            downsample=True,
                            facecolor='whitesmoke',
                            loc='best'):
    """
    Fama-French模型因子变化趋势与对比
    参数：
    model：模型，默认'FF3'，可选'FF3'、'FF5'和'Mom'
        'ST_Rev'和'LT_Rev'仅支持美国
    indicator：因子，默认'SMB'
        FF3可选'Mkt-RF'、'SMB'、'HML'
        FF5可选'Mkt-RF'、'SMB'、'HML'、'CMA'、'RMW'
        Mom仅可选'Mom'，ST_Rev仅可选'ST_Rev'，LT_Rev仅可选'LT_Rev'

    market：市场或经济体，默认'US'
        可选'US'、'Japan'、'Europe'、'China'（中国为大致估计数）
        以及EM（新兴市场）、DM（发达经济体）、DM_ex_US（发达经济体（除美国外））
    start：开始日期，默认'L5Y'
    end：结束日期，默认'today'
    frequency：因子频度，默认'monthly'
        可选'daily'、'monthly'、'annual'
    cumulative：是否使用因子的累计收益率，默认True，不累计为False
    TTM；展示动态趋势时是否进行移动平均，默认True，不进行移动平均为False
    annotate：是否在曲线末尾进行标注，默认True，不标注为False
    """
    
    # 映射原变量
    factor=model
    scope=market
    col=indicator
    freq=frequency
    
    # 检查参数
    factor_list=['FF3','FF5','Mom','ST_Rev','LT_Rev']
    if factor not in factor_list:
        print(f"  Invalid model {factor}, must be one of {factor_list}")
        return

    freq_list=['daily','monthly','annual']
    if freq not in freq_list:
        print(f"  Invalid frequency {freq}, must be one of {freq_list}")
        return
    if freq == 'annual': freq='yearly'
        
    scope_list=['US','EU','Europe','JP','Japan','CN','China', \
                'DM','Developed_Market','DM_ex_US','Developed_ex_US', \
                'EM','Emerging_Market','NA','North_America','GL','Global', \
                'GL_ex_US','Global_ex_US']
    if isinstance(scope,str):
        if scope not in scope_list:
            print(f"  Unsuported market {scope} for FF asset pricing models")
            print(f"  Supported markets {scope_list}")
            return

    if isinstance(scope,list):
        for s in scope:
            if s not in scope_list:
                print(f"  Unsuported market {s} for FF asset pricing models")
                print(f"  Supported markets {scope_list}")
                return

    col_list=['Mkt-RF','SMB','HML','CMA','RMW','Mom','ST_Rev','LT_Rev']
    if isinstance(col,str):
        if col in ['MOM','Mom']: col=factor='Mom'
        if col in ['ST-Rev','ST-REV','ST_Rev','ST_REV']: col=factor='ST_Rev'
        if col in ['LT-Rev','LT-REV','LT_Rev','LT_REV']: col=factor='LT_Rev'
        if col in ['Mkt-RF','Mkt_RF','MKT-RF','MKT_RF']: col='Mkt-RF'
        
        if col not in col_list:
            print(f"  Unsuported indicator {col} for FF asset pricing models")
            print(f"  Supported indicators {col_list}")
            return

    if isinstance(col,list):
        for c in col:
            if c in ['MOM','Mom']: 
                if col in ['MOM','Mom']: col=factor='Mom'; break
                if col in ['ST-Rev','ST-REV','ST_Rev','ST_REV']: col=factor='ST_Rev'; break
                if col in ['LT-Rev','LT-REV','LT_Rev','LT_REV']: col=factor='LT_Rev'; break
            
            if c not in col_list:
                print(f"  Unsuported indicator {c} for FF asset pricing models")
                print(f"  Supported indicators {col_list}")
                return
    
    # 转换日期
    start,end=start_end_preprocess(start,end)
        
    # 单个因子
    #if isinstance(col,list) and len(col) == 1: col=col[0]
    if isinstance(col,str):
        
        if isinstance(scope,str):
            scope=[scope]
        if not cumulative:
            result=compare_ff_factors(start, end, scopes=scope, factor=factor, \
                                      freq=freq, col=col,TTM=TTM, \
                                      annotate=annotate, \
                                          downsample=downsample, \
                                          facecolor=facecolor,loc=loc)
        else:
            result=compare_ff_cumulative(start, end, scopes=scope, factor=factor, \
                                         freq=freq, col=col, \
                                         annotate=annotate, \
                                             downsample=downsample, \
                                             facecolor=facecolor,loc=loc)
    
    # 多个因子
    #if isinstance(col,list) and (len(col) > 1):
    if isinstance(col,list):
        if isinstance(scope,list):
            scope=scope[0]
            
        if not cumulative:
            result=plot_ff_factors(start, end, scope=scope, factor=factor, \
                                   freq=freq, cols=col,TTM=TTM, \
                                   annotate=annotate, \
                                       downsample=downsample, \
                                       facecolor=facecolor,loc=loc)
        else:
            result=compare_factors_cumulative_single_country(start, end, \
                                scope=scope, factor=factor, freq=freq, \
                                cols=col,annotate=annotate, \
                                    downsample=downsample, \
                                    facecolor=facecolor,loc=loc)
                
    return result
        
        
    
#==============================================================================


class SuppressPlots:
    """
    在Jupyter中运行时阻止matplotlib显示图像
    在VSCode和PyCharm中未测试！！！
    """
    def __enter__(self):
        # 记录状态
        self._interactive = plt.isinteractive()
        self._orig_show = plt.show

        # 关闭交互 + 拦截 show
        plt.ioff()
        plt.show = lambda *args, **kwargs: None

        # 记录并屏蔽 Figure 的富显示与 repr
        # 不同环境下这些方法是否存在不一定，所以逐一保存与屏蔽
        self._orig_repr = getattr(Figure, "__repr__", None)
        self._orig_repr_png = getattr(Figure, "_repr_png_", None)
        self._orig_repr_svg = getattr(Figure, "_repr_svg_", None)
        self._orig_repr_html = getattr(Figure, "_repr_html_", None)

        def _noop(*args, **kwargs):
            return None
        def _empty_str(*args, **kwargs):
            return ""

        if self._orig_repr is not None:
            Figure.__repr__ = _empty_str
        if self._orig_repr_png is not None:
            Figure._repr_png_ = _noop
        if self._orig_repr_svg is not None:
            Figure._repr_svg_ = _noop
        if self._orig_repr_html is not None:
            Figure._repr_html_ = _noop

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭所有图，避免残留在下一单元被回显
        try:
            plt.close('all')
        except Exception:
            pass

        # 恢复 show 与交互模式
        plt.show = self._orig_show
        if self._interactive:
            plt.ion()
        else:
            plt.ioff()

        # 恢复 Figure 的表示方法
        if self._orig_repr is not None:
            Figure.__repr__ = self._orig_repr
        if self._orig_repr_png is not None:
            Figure._repr_png_ = self._orig_repr_png
        if self._orig_repr_svg is not None:
            Figure._repr_svg_ = self._orig_repr_svg
        if self._orig_repr_html is not None:
            Figure._repr_html_ = self._orig_repr_html

        return False  # 让异常正常传播

#==============================================================================


if __name__=='__main__':
    model=['FF3','Mom','ST_Rev','LT_Rev','FF5']
    indicator=['SMB','HML','Mom','ST_Rev','LT_Rev']
    market='US'
    start='L5Y'; end='today'
    frequency='monthly'
    cumulative=True
    TTM=True
    annotate=True
    loc='best'
    
    
def security_trend_fffactor(model='FF3',
                            indicator='SMB',
                            market='US',
                            start='L5Y',end='today',
                            frequency='monthly',
                            cumulative=True,
                            TTM=True,
                            annotate=True,
                            downsample=True,
                            facecolor='whitesmoke',
                            loc='best'):
    """
    Fama-French模型因子变化趋势与对比
    参数：
    model：模型，默认'FF3'，可选'FF3'、'FF5'和'Mom'
        'ST_Rev'和'LT_Rev'仅支持美国
    indicator：因子，默认'SMB'
        FF3可选'Mkt-RF'、'SMB'、'HML'
        FF5可选'Mkt-RF'、'SMB'、'HML'、'CMA'、'RMW'
        Mom仅可选'Mom'，ST_Rev仅可选'ST_Rev'，LT_Rev仅可选'LT_Rev'

    market：市场或经济体，默认'US'
        可选'US'、'Japan'、'Europe'、'China'（中国为大致估计数）
        以及EM（新兴市场）、DM（发达经济体）、DM_ex_US（发达经济体（除美国外））
    start：开始日期，默认'L5Y'
    end：结束日期，默认'today'
    frequency：因子频度，默认'monthly'
        可选'daily'、'monthly'、'annual'
    cumulative：是否使用因子的累计收益率，默认True，不累计为False
    TTM；展示动态趋势时是否进行移动平均，默认True，不进行移动平均为False
    annotate：是否在曲线末尾进行标注，默认True，不标注为False
    """
    
    # 单模型情形
    if isinstance(model,list) and len(model)==1:
        model=model[0]
    
    if isinstance(model,str):
        result=security_trend_fffactor_1model(model=model,
                                    indicator=indicator,
                                    market=market,
                                    start=start,end=end,
                                    frequency=frequency,
                                    cumulative=cumulative,
                                    TTM=TTM,
                                    annotate=annotate,
                                    downsample=downsample,
                                    facecolor=facecolor,
                                    loc=loc)
        return result
    
    # 多模型情形
    df=pd.DataFrame()
    model_list=model
        
    for mod in model_list:
        # 用于筛选适合mod的indicator
        mod_indicator=[]
        
        if isinstance(indicator,str):
            indicator_list=[indicator]
        else:
            indicator_list=indicator
            
        if mod in ['FF3']:
            mod_ind_all=['Mkt-RF','SMB','HML']
        elif mod in ['FF5']:
            mod_ind_all=['Mkt-RF','SMB','HML','RMW','CMA']
        elif mod in ['Mom','ST_Rev','LT_Rev']:
            mod_ind_all=[mod]
        else:
            print(f"  Unsupported model {mod} for FF asset pricing models")
            continue
            
        for ind in indicator_list:
            if ind in mod_ind_all:
                mod_indicator=mod_indicator+[ind]
        
        # 其他参数均设置为单项
        if isinstance(market,list):
            mod_market=market[0]
        else:
            mod_market=market
                    
        if isinstance(frequency,list):
            mod_frequency=frequency[0]
        else:
            mod_frequency=frequency

        # 在 Jupyter 中调用时屏蔽绘图
        with SuppressPlots():
            # 注意：数据为百分数，cumulative时已经减去1为累计增长率
            dftmp=security_trend_fffactor_1model(model=mod,
                                        indicator=mod_indicator,
                                        market=mod_market,
                                        start=start,end=end,
                                        frequency=mod_frequency,
                                        cumulative=cumulative,
                                        TTM=TTM,
                                        annotate=annotate,
                                        downsample=downsample,
                                        loc=loc)
        if dftmp is None: continue        
        
        dftmp_cols=list(dftmp)
        for tmp_col in dftmp_cols:
            if tmp_col != mod:
                new_col=mod+'.'+tmp_col
                dftmp.rename(columns={tmp_col:new_col},inplace=True)
            else:
                new_col=tmp_col
        
        if len(df) == 0:
            df=dftmp
        else:
            df=df.join(dftmp,how='outer')
    
    if len(df) == 0:
        print(f"  Sorry, no FF model factors found, consider revise the parameters")
        return df
    
    scope_txt,freq_txt=translate_scope_freq(market,frequency)
    
    axhline_label='零线'
    if cumulative:
        y_label=text_lang("模型因子累计增长率（%）","Model Factor Cumulative Growth (%)")
        axhline_value=0
    else:
        y_label=text_lang("模型因子（%）","Model Factor (%)")
        axhline_value=0
    
    # 倒算年化复合增长率
    ft0=''
    if cumulative:
        dftmp=df / 100.0 + 1
        for c_pct in list(dftmp):
            CAGR=cagr(dftmp,indicator=c_pct,printout=False)
            CAGR_pct=srounds(CAGR * 100)
            
            if ft0 == '':
                ft0_comma=''
            else:
                ft0_comma=text_lang('，',', ')
            ft0=ft0+ft0_comma+text_lang(f"{c_pct}：年化{CAGR_pct}%",f"{c_pct}: {CAGR_pct}% p.a.")
            
    
    import datetime; todaydt = datetime.date.today()
    ft1_cn=f"数据来源：Fama/French Forum，"+str(todaydt)
    ft1_en=f"Data source: Fama/French Forum, "+str(todaydt)
    ft1=text_lang(ft1_cn,ft1_en)
    
    if ft0 == '':
        x_label=ft1
    else:
        x_label=ft0 +'\n'+ ft1

    if cumulative:
        title_cn=f"FF模型{freq_txt}因子累计增长率走势：{scope_txt}"
        title_en=f"FF Model {freq_txt.title()} Factor Cumulative Growth Trend: {scope_txt}"
    elif TTM:
        title_cn=f"FF模型{freq_txt}因子TTM走势：{scope_txt}"
        title_en=f"FF Model {freq_txt.title()} Factor TTM Trend: {scope_txt}"
    else:
        title_cn=f"FF模型{freq_txt}因子走势：{scope_txt}"
        title_en=f"FF Model {freq_txt.title()} Factor Trend: {scope_txt}"
        
    title_txt=text_lang(title_cn,title_en)

    # 降采样，稀疏化(sparse matrix)，避免绘制的折线过于密集
    if downsample:
        # 对所有数值型字段进行重采样
        dfsm=auto_downsample(df)
    else:
        dfsm=df
    
    draw_lines(dfsm,y_label,x_label,axhline_value,axhline_label,title_txt, \
            linewidth=1.5, \
            band_area='',loc=loc, \
            annotate=annotate,annotate_value=annotate,plus_sign=False, \
            attention_value='',attention_value_area='', \
            attention_point='',attention_point_area='', \
            mark_start=False,mark_top=False,mark_bottom=False,mark_end=False, \
            facecolor=facecolor)
    
    return df
#==============================================================================




















