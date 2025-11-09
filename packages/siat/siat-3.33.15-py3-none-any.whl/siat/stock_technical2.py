# -*- coding: utf-8 -*-
"""
本模块功能：股票技术分析德宏图
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年10月30日
最新修订日期：2025年10月30日
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
from siat.grafix import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.stock import *
from siat.valuation import *
from siat.stock_technical import *
#==============================================================================
import pandas as pd
import numpy as np

#==============================================================================
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=18
ylabel_txt_size=14
xlabel_txt_size=14
legend_txt_size=14
annotate_txt_size=12

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 

#设置绘图风格：关闭网格虚线
plt.rcParams['axes.grid']=False

#==============================================================================
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ =="__main__":
    RSI_days=[6,24]; OBV_days=[5,10]
    MA_days=[5,20]; EMA_days=[5,20]
    MACD_fastperiod=12; MACD_slowperiod=26; MACD_signalperiod=9
    KDJ_fastk_period=5; KDJ_slowk_period=3; KDJ_slowk_matype=0; KDJ_slowd_period=3; KDJ_slowd_matype=0
    VOL_fastperiod=5; VOL_slowperiod=10
    PSY_days=12; ARBR_days=26
    CR_day=16; CR_madays=[5,10,20]
    EMV_day=14; EMV_madays=9
    BOLL_days=20; BOLL_nbdevup=2; BOLL_nbdevdn=2; BOLL_matype=0
    TRIX_day=12; TRIX_madays=20
    DMA_fastperiod=10; DMA_slowperiod=50; DMA_madays=10
    BIAS_days=[6,12,24]; CCI_days=[6,12]; WR_days=[10,6]
    ROC_day=12; ROC_madays=6
    DMI_DIdays=14; DMI_ADXdays=6
    MFI_day=14; MFI_madays=[6]
    MOM_day=12; MOM_madays=6
    SAR_day=4; SAR_madays=[5,20]
    BETA_day=5; BETA_madays=[5,20]
    TSF_day=14; TSF_madays=[5,10]
    AD_madays=[5]
    
    ticker='600519.SS';ticker_type='auto'; source='auto'
    start='2024-5-1'; end='2024-7-13'; ahead_days=30*8
    technical='MACD'; indicator='Close'
    
    annotate=True; annotate_value=True
    #注意：annotate_va_list的个数要么为1要么与绘制的曲线个数相同
    annotate_va_list=["center"]; annotate_ha="left"
    #注意：va_offset_list基于annotate_va上下调整，其个数为1或与绘制的曲线个数相同
    va_offset_list=[0]
    annotate_bbox=False; bbox_color='whitesmoke'
    
    attention_value=[0,25,50,75]
    more_details=True
    resample_freq='6H'; smooth=True;linewidth=1.5
    date_range=False; date_freq=False; annotate=False
    graph=['ALL']; printout=False; loc1='best'; loc2='best'
        
    facecolor=['whitesmoke','papayawhip']; canvascolor='whitesmoke'
    price_line_color=['red','green']; price_line_width=5; price_line_marker=['^',"v"]
    marker_sizes=[30,120,250]; marker_mode='auto'
    
    df=security_technical2(ticker='AAPL',start='2024-5-1',end='2024-6-20', \
                           technical='CR',more_details=True,loc1='upper left',loc2='lower right')
    
    #逐个测试
    tlist=['RSI','OBV','MACD','KDJ','VOL','PSY','ARBR','CR','EMV','Bollinger', \
           'TRIX','DMA','BIAS','CCI','W%R','ROC','DMI']
    for t in tlist:
        df=security_technical2(ticker,start,end,technical=t,loc1='lower left',loc2='lower right')
    
def security_technical2(ticker,start='default',end='default',technical='MACD', \
                            
        #不建议使用复权价，因为最高最低价开盘价不易获取到复权价！    
        indicator='Close', \
            
        #显示指标本身，如果原来未显示的话
        more_details=False, \
            
        #显示关注值水平线，每个指标不同，可自定义多个关注值
        attention_value=[], \

        ticker_type='auto',source='auto', \
        
        #指标的默认参数
        RSI_days=[6,14], OBV_days=[5,10], \
        
        MA_days=[5,20],EMA_days=[5,20], \
        MACD_fastperiod=12,MACD_slowperiod=26,MACD_signalperiod=9, \
        
        KDJ_fastk_period=9,KDJ_slowk_period=5,KDJ_slowk_matype=1,KDJ_slowd_period=5,KDJ_slowd_matype=1, \
        
        VOL_fastperiod=5,VOL_slowperiod=10, \
            
        PSY_days=[6,12], ARBR_days=[26], \
            
        CR_day=30,CR_madays=[10,20,40,60], \
            
        EMV_day=14,EMV_madays=[9], \
        
        BOLL_days=20,BOLL_nbdevup=2,BOLL_nbdevdn=2,BOLL_matype=0, \
        
        DMA_fastperiod=10,DMA_slowperiod=50,DMA_madays=[10], \
        
        TRIX_day=12,TRIX_madays=[20], \
            
        BIAS_days=[6,12,24], CCI_days=[6,12], WR_days=[13,34,89], \
            
        ROC_day=12,ROC_madays=[65,12,18], \
            
        DMI_DIdays=7,DMI_ADXdays=6, \
        
        #资金流：
        MFI_day=14,MFI_madays=[6], \
            
        MOM_day=12,MOM_madays=6, \
            
        #需要显示SAR
        SAR_day=4,SAR_madays=[5,20], \
            
        #需要显示BETA
        BETA_day=5,BETA_madays=[5,20], \
        
        #需要显示TSF
        TSF_day=14,TSF_madays=[5,10], \
            
        #需要显示AD
        AD_madays=[], \
        
        #数据提前量，用于前置计算指标的移动平均值   
        ahead_days=30*8, \
            
        #指标线的绘图参数
        resample_freq='2H',smooth=True,linewidth=1.5, \
        date_range=False,date_freq=False, \
            
        #启用，替代loc1图例，不替代loc2图例
        annotate=True,annotate_value=True,
        #注意：annotate_va_list的个数要么为1要么与绘制的曲线个数相同
        annotate_va_list=["center"],annotate_ha="left",
        #注意：va_offset_list基于annotate_va上下调整，其个数为1或与绘制的曲线个数相同
        va_offset_list=[0],
        annotate_bbox=False,bbox_color='black', \
        
        #除了MACD外，其他指标均应为ALL
        graph=['ALL'], printout=False, loc1='best',loc2='best', \
            
        #假设红涨绿跌
        price_line_color=['red','green'], \
        
        #图形上下半区的背景颜色，画布背景颜色
        facecolor=['papayawhip','papayawhip'], canvascolor='whitesmoke',
        price_line_width=3, price_line_marker=['^',"v"], 
        #marker_sizes=[30,120,250], \
        
        marker_mode='auto', #可选'auto','all','big','none'
        
        show_volume=True, #是否显示成交量
        
        DEBUG=False,
        ):
    """
    ===========================================================================
    功能：技术分析指标的短线德宏图，建议两个月内，适合观察日差价和价量关系变化，图示简洁。
    主要参数：
    ticker：证券代码，除美股外需要交易所后缀，例如港股小米'01810.HK'，美股苹果'AAPL'
    start：开始日期，格式YYYY-MM-DD，默认一个月前
    end：结束日期，格式与start相同，默认已收盘的最近交易日
    technical：技术分析指标，默认为MACD，单次仅可指定一个指标。支持的指标如下：
        Bollinger：布林带，MACD：移动异同平均线，RSI：相对强弱
        KDJ：随机指标，OBV：能量潮，SAR：抛物线/停损转向指标
        VOL：成交量指标，ARBR：人气(AR)/意愿(BR)指标
        CR：中间意愿指标，EMV：简易波动，TRIX：三重指数平滑均线
        DMA：均线差，BIAS：乖离率，CCI：顺势指标，W%R：威廉超买/超卖指标
        ROC：变动率，DMI：动向指标，PSY：心理线，MFI：资金流向指标
        MOM：动量指标，BETA：移动贝塔系数，TSF：时间序列分析
        AD：集散指标，MA：简单移动平均，EMA：指数移动平均

    RSI_days：默认[6,14]        
    OBV_days：默认[5,10]    
    MA_days：默认[5,20]
    EMA_days：默认[5,20]；EMV_day：默认14：EMV_madays：默认[9]    
    MACD_fastperiod：默认12；MACD_slowperiod：默认26；MACD_signalperiod：默认9      
    KDJ_fastk_period：默认9；KDJ_slowk_period：默认5；KDJ_slowk_matype：默认1
    KDJ_slowd_period：默认5；KDJ_slowd_matype：默认1    
    VOL_fastperiod：默认5；VOL_slowperiod：默认10        
    PSY_days：默认[6,12]        
    ARBR_days：默认[26]        
    CR_day：默认30；CR_madays：默认[10,20,40,60]    
    BOLL_day：默认20；BOLL_nbdevup：默认2；BOLL_nbdevdn：默认2；BOLL_matype：默认0    
    DMA_fastperiod：默认10；DMA_slowperiod：默认50；DMA_madays：默认[10]
    TRIX_day：默认12；TRIX_madays：默认[20]        
    BIAS_days：默认[6,12,24]        
    CCI_days：默认[6,12]        
    WR_days：默认[13,34,89]        
    ROC_day：默认12；ROC_madays：默认[65,12,18]        
    DMI_DIdays：默认7；DMI_ADXdays：默认6    
    MFI_day：默认14；MFI_madays：默认[6]
    MOM_day：默认12；MOM_madays：默认6        
    SAR_day：默认4；SAR_madays：默认[5,20]        
    BETA_day：默认5；BETA_madays：默认[5,20]    
    TSF_day：默认14；TSF_madays：默认[5,10]        
    AD_madays：默认[]
    
    more_details：显示指标本身，如果原来未显示的话。默认不显示
    attention_values：显示关注值水平线，每个技术指标可能不同，可使用列表自定义多个关注值
    ticker_type：证券类别，默认'auto'。如果识别错误,可强制指定'stock'、'bond'、'fund'
    source：证券价格来源，默认'auto'。特殊来源可自行指定

    loc1：第1个图例的位置，默认'best'。当annotate=True时被替代
    loc2：第2个图例的位置，默认'best'。可手动指定9个位置，例如'upper left'左上角等
    facecolor：图形上下半区的背景颜色，默认['whitesmoke','papayawhip']
    
    下列指标可以使用强化指令security_technical：MACD、RSI、KDJ、Bollinger
    """
    #放在入口参数容易产生奇怪的上次运行记忆效应，暂时强制写死在这里
    marker_sizes=[45,90,180]
    
    #检查marker_sizes的奇怪错误，难道有上次运行的记忆残留？
    marker_sizes_original=marker_sizes.copy()
    if DEBUG:
        print("===== DEBUG starts 0 =====")
        print(f"marker_mode={marker_mode}, marker_sizes={marker_sizes_original}")
        print("===== DEBUG ended 0 =====")
    
    #偷懒式重定义，保持与其他指令参数名称的一致性，又不修改本程序
    attention_values=attention_value
    
    # 检查ta-lib是否安装，避免浪费后续的处理
    try:
        import talib  
    except:
        print("  #Error(security_technical2): lack of necessary package - talib")
        talib_install_method()
        return None
    
    #检查证券代码
    if not isinstance(ticker,str):
        print("  #Warning(security_technical2): not a security code for",ticker)
        return None        

    #检查indicator
    if indicator not in ['Open','Close','High','Low','Adj Close']:
        print("  #Warning(security_technical2): not a valid price type for",indicator)
        return None        
        
    #检查日期：如有错误自动更正
    fromdate,todate=start_end_preprocess(start=start,end=end)
    
    #检查指标类别
    tech_list={'Bollinger':text_lang('布林带','Bollinger Bands'), \
               #'MACD':text_lang('移动异同平均线','Moving Average Convergence Divergence'), \
               'MACD':text_lang('MACD','MACD'), \
               'RSI':text_lang('相对强弱','Relative Strength Index'), \
               'KDJ':text_lang('随机指标','Stochastics'), \
               'OBV':text_lang('能量潮','On-Balance-Volume'), \
               'SAR':text_lang('抛物线/停损转向指标','Stop and Reverse Indicator'), \
               'VOL':text_lang('成交量指标','Volume Indicator'), \
               'ARBR':text_lang('人气(AR)意愿(BR)指标','Emotion AR & Willingness BR'), \
               'CR':text_lang('中间意愿指标','Commodity Channel Index Reversal'), \
               'EMV':text_lang('简易波动','Ease of Movement Value'), \
               'TRIX':text_lang('三重指数平滑均线','Triple Exponentially Smoothed Moving Average'), \
               'DMA':text_lang('均线差','Difference in Moving Averages'), \
               'BIAS':text_lang("乖离率",'Bias Indicator'), \
               'CCI':text_lang('顺势指标','Commodity Channel Index'), \
               'W%R':text_lang('威廉超买/超卖指标','William Overbought/Oversold Index'), \
               'ROC':text_lang('变动率','Rate of Change'), \
               'DMI':text_lang('动向指标','Directional Movement Index'), \
               'PSY':text_lang('心理线','Phycholoigical Line'), \
               'MFI':text_lang('资金流向指标','Money Flow Index'), \
               'MOM':text_lang('动量指标','Momentum'), \
               'BETA':text_lang("移动贝塔系数",'Moving Beta Coefficient'), \
               'TSF':text_lang("时间序列分析",'Time Series Forecasting'), \
               'AD':text_lang('集散指标','Accumulation/Distribution'), \
               'MA':text_lang('简单移动平均','Moving Average'), \
               'EMA':text_lang('指数移动平均','Exponential Moving Average')}

    #仅支持一个技术分析指标
    technical1=technical
    if isinstance(technical,list):
        technical1=technical[0]
    technical1=technical1.upper()
    if technical1 == 'BOLLINGER': technical1=technical1.title()

    if technical1 not in list(tech_list):
        print("  #Warning(security_technical2): unsupported technical pattern",technical)
        print("  Supported patterns:",list(tech_list))
        return None        
        
    #抓取抓取价格数据
    fromdate1=date_adjust(fromdate,adjust=-ahead_days)
    if 'Adj' in indicator.title():
        adjust='Adj_only' #最高最低价开盘收盘价均为复权价
    else:
        adjust=''
        
    price,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate1,adjust=adjust, \
                                        todate=todate,ticker_type=ticker_type,fill=False,source=source)

    if found not in ['Found']:
        print("  #Warning(security_technical2): no prices found for",ticker,'as type',ticker_type)
        return None        

    #当日涨跌
    price['up_down']=price['Close']-price['Open']
    price['up_down_abs']=abs(price['up_down'])
    
    #期间内每日涨跌幅分位数：高（70%及以上），低（30%及以下），中（30%~70%）
    #按照预定的期间确定分位数，并非对扩展的区间
    price_disp=price.loc[fromdate:todate]
    price_num=len(price_disp)
    q70=np.percentile(price_disp['up_down_abs'],70)
    q30=np.percentile(price_disp['up_down_abs'],30)
    
    # 判断marker_mode，决定如何显示marker
    if DEBUG:
        print("===== DEBUG starts 1 =====")
        print(f"price_num={price_num}, marker_mode={marker_mode}, marker_sizes={marker_sizes_original}")
        print("===== DEBUG ended 1 =====")
    
    marker_mode=marker_mode.lower()
    if not (marker_mode in ['all']):
        if marker_mode in ['auto']:
            if price_num > 132:
                marker_sizes=[0,0,0]
            elif price_num > 66:
                marker_sizes[0]=0; marker_sizes[1]=0; marker_sizes[2]=marker_sizes_original[2]
            else:
                marker_sizes=marker_sizes_original

        if marker_mode in ['big']:
            marker_sizes[0]=0; marker_sizes[1]=0; marker_sizes[2]=marker_sizes_original[2]

        if marker_mode in ['mid-big']:
            marker_sizes[0]=0; marker_sizes[1]=marker_sizes_original[1]
            marker_sizes[2]=marker_sizes_original[2]

        if marker_mode in ['none']:
            marker_sizes=[0,0,0]
    else:
        marker_sizes=marker_sizes_original

    if DEBUG:
        print("===== DEBUG starts 2 =====")
        print(f"price_num={price_num}, marker_mode={marker_mode}, marker_sizes={marker_sizes}")
        print("===== DEBUG ended 2 =====")
        
    small_size=marker_sizes[0]; mid_size=marker_sizes[1]; big_size=marker_sizes[2]
    price['marker_size']=price['up_down_abs'].apply(lambda x: big_size if x>=q70 else small_size if x<=q30 else mid_size)
    
    #计算技术指标：返回的df区间为预期的时间段
    df,calculated=calc_technical(price,fromdate,todate,technical=technical, \
                          
            RSI_days=RSI_days, \
            OBV_days=OBV_days, \
                
            MA_days=MA_days,EMA_days=EMA_days, \
                
            MACD_fastperiod=MACD_fastperiod,MACD_slowperiod=MACD_slowperiod,MACD_signalperiod=MACD_signalperiod, \
                
            KDJ_fastk_period=KDJ_fastk_period,KDJ_slowk_period=KDJ_slowk_period, \
            KDJ_slowk_matype=KDJ_slowk_matype,KDJ_slowd_period=KDJ_slowd_period,KDJ_slowd_matype=KDJ_slowd_matype, \
                
            VOL_fastperiod=VOL_fastperiod,VOL_slowperiod=VOL_slowperiod, \
                
            PSY_days=PSY_days, \
            ARBR_days=ARBR_days, \
            CR_day=CR_day,CR_madays=CR_madays, \
            EMV_day=EMV_day,EMV_madays=EMV_madays, \
                
            BOLL_days=BOLL_days,BOLL_nbdevup=BOLL_nbdevup,BOLL_nbdevdn=BOLL_nbdevdn,BOLL_matype=BOLL_matype, \
                
            DMA_fastperiod=DMA_fastperiod,DMA_slowperiod=DMA_slowperiod,DMA_madays=DMA_madays, \
                
            TRIX_day=TRIX_day,TRIX_madays=TRIX_madays, \
            BIAS_days=BIAS_days, \
            CCI_days=CCI_days, \
            WR_days=WR_days, \
            ROC_day=ROC_day,ROC_madays=ROC_madays, \
            DMI_DIdays=DMI_DIdays,DMI_ADXdays=DMI_ADXdays, \
                
            MFI_day=MFI_day,MFI_madays=MFI_madays, \
            MOM_day=MOM_day,MOM_madays=MOM_madays, \
                
            #需要显示SAR
            SAR_day=SAR_day,SAR_madays=SAR_madays, \
                
            #需要显示BETA
            BETA_day=BETA_day,BETA_madays=BETA_madays, \
            
            #需要显示TSF
            TSF_day=TSF_day,TSF_madays=TSF_madays, \
                
            #需要显示AD
            AD_madays=AD_madays, \
            
            indicator=indicator, \
            more_details=more_details)

    #技术指标的绘图线
    tech_line_default={'RSI':['rsi'],
                    'OBV':['obv'],
                    'MACD':['DIF','DEA'],
                    'KDJ':['kdj'],
                    'SAR':['sar'],
                    'VOL':['vol'],
                    'PSY':['psy'],
                    'ARBR':['ar','br'],
                    'CR':['cr'],
                    'EMV':['emv'],
                    'Bollinger':['upper','mid','lower'],
                    'TRIX':['trix'],
                    'BIAS':['bias'],
                    'CCI':['cci'],
                    'W%R':['wr'],
                    'ROC':['roc'],
                    'DMI':['pdi','mdi'],
                    'DMA':['dma'],
                    'MFI':['mfi'],
                    'MOM':['mom'],
                    'BETA':['beta'],
                    'TSF':['tsf'],
                    'AD':['ad'],
                    'MA':['ma'],'EMA':['ema'],
                    }
        
    #检查计算结果：有问题？
    if not calculated:
        print("  #Warning(security_technical2): unsupported technical parameter",technical)
        print("  Supported technical parameters:")
        printlist(sorted(list(tech_line_default.keys())),numperline=11,beforehand='  ',separator=' ')
        return None
    
    #绘图数值缩放比例，以便使指标数量级与股价更加协调
    magnitude_list={'RSI':[1,''],
                    'OBV':[1/1000000,text_lang('百万','in millions')],
                    'MACD':[1,''],
                    'KDJ':[1,''],
                    'SAR':[1,''],
                    'VOL':[1/1000000,text_lang('百万','in millions')],
                    'PSY':[1,''],
                    'ARBR':[1,''],
                    'CR':[1,''],
                    'EMV':[1000000000,text_lang('十亿分之一','in 1 billionth')],
                    'Bollinger':[1,''],
                    'TRIX':[100,text_lang('百分之一','%')],
                    'BIAS':[1,''],
                    'CCI':[1,''],
                    'W%R':[1,''],
                    'ROC':[1,''],
                    'DMI':[1,''],
                    'DMA':[1,''],
                    'MA':[1,''],
                    'EMA':[1,''],
                    'MFI':[1,''],
                    'MOM':[1,''],
                    'BETA':[1,''],
                    'TSF':[1,''],
                    'AD':[1/1000000,text_lang('百万','in millions')],
                    'Volume':[1/1000000,text_lang('百万','in millions')]}

    mag_times=magnitude_list[technical1][0]
    mag_label=magnitude_list[technical1][1]
    
    if  'ALL' in graph or 'all' in graph or 'All' in graph:
        tech_line_prefix=tech_line_default[technical1]
    else:
        if not isinstance(graph,list):
            tech_line_prefix=[graph]
        else:
            tech_line_prefix=graph
        
    tech_line_collist=[]
    df_collist=list(df)
    for p in tech_line_prefix:
        for c in df_collist:
            if p in c:
                tech_line_collist=tech_line_collist+[c]
    #去掉重复项
    tech_line_collist=list(set(tech_line_collist))
    #去掉误选项
    if technical1 == 'ARBR':
        remove_cols=[]; remove_item='sar'
        for c in tech_line_collist:
            if remove_item in c:
                tech_line_collist.remove(c)

    #改变测度
    for c in tech_line_collist:
        df[c]=df[c] * mag_times

    df['Volume']=df['Volume'] * magnitude_list['Volume'][0]
    
    #确保用于绘图的df1包含必要的字段
    if 'marker_size' in tech_line_collist:
        df1=df[tech_line_collist+[indicator,'Volume','up_down']]
    else: 
        df1=df[tech_line_collist+[indicator,'Volume','up_down','marker_size']]
    
    #绘图：技术分析指标----------------------------------------------------------
    print('') #距离上条信息空一行
    #指标与价格属于同一数量级，不易绘制双轴图，否则会导致奇怪图示，并影响看图讲故事
    tech_close_same_list=['MA','EMA','Bollinger','SAR','TSF']
    
    # 创建两行的布局，上半部分高度为4，下半部分高度为1
    fig = plt.figure(figsize=(14,9))
    
    if isinstance(facecolor,str):
        facecolor1=facecolor2=facecolor
    elif isinstance(facecolor,list):
        if len(facecolor) >= 2:
            facecolor1=facecolor[0]
            facecolor2=facecolor[1]
        elif len(facecolor) == 1:
            facecolor1=facecolor2=facecolor[0]
    else:
        facecolor1='whitesmoke'; facecolor2='papayawhip'
    
    gs = fig.add_gridspec(2, 1, height_ratios=[4, 1], hspace=0.05)
    ax = fig.add_subplot(gs[0])
    try:
        ax.set_facecolor(facecolor1)
    except:
        ax.set_facecolor('whitesmoke')
        
    color_list=['k','g','b','c','m','yellowgreen','tomato','lime','orange','deepskyblue']
    
    if isinstance(attention_values,int):
        attention_values=[attention_values]
    attention_draws=[False] * len(attention_values)

    #技术分析线型：不用于绘制价格线
    linestyles = ["dotted", "dashed", "dashdot", "longdash", "longdashdot"]
    
    #基于df1中tech_line_collist列最新值的大小降序排列tech_line_collist
    #目的是配合offset_va的调整顺序，否则使用offset_va时将会对应错乱！
    _, tech_line_collist = sort_display_columns_by_latest(df1, tech_line_collist)
    
    for l in tech_line_collist:
        if l == 'marker_size': continue
        
        lpos=tech_line_collist.index(l)
        
        #设置折线终点标记
        labeltxt=l.upper()
        if labeltxt =='DEA':
            labeltxt=text_lang('慢线(DEA)','DEA (Slow line)')
        if labeltxt =='DIF':
            labeltxt=text_lang('快线(DIF)','DIF (Fast line)')      
            
        if labeltxt =='UPPER':
            labeltxt=text_lang('上线','Upper Line')      
        if labeltxt =='MID':
            labeltxt=text_lang('中线','Mid Line')      
        if labeltxt =='LOWER':
            labeltxt=text_lang('下线','Lower Line')      
            
        #绘制技术指标
        axline, = ax.plot(df1.index,df1[l],label=labeltxt,ls=linestyles[lpos])
        last_line_color = axline.get_color()
        
        #标记终点文字，必要时可手动调整纵向偏移和横向左右位置，避免扎堆互相重叠
        if annotate:
            df_end=df1.tail(1)
            end_value=df_end[l].values[0]
            # df_end[c]必须为数值类型，否则可能出错
            y_end = df_end[l].min()    # 末端的y坐标
            x_end = df_end[l].idxmin() # 末端值的x坐标 

            if annotate_value:
                if technical1 in tech_close_same_list:
                    ann_text=f" {labeltxt}({srounds(end_value)})"
                else:
                    ann_text=f"{labeltxt}\n({srounds(end_value)})"
            else:
                ann_text=f" {labeltxt}"
            
            # 灵活调整annotate_va，调整纵向偏移
            if len(annotate_va_list) == 1:
                annotate_va=annotate_va_list[0]
            else:
                try:
                    annotate_va=annotate_va_list[lpos]
                except:
                    annotate_va='center'

            # 灵活调整va_offset
            try:
                va_offset=va_offset_list[lpos]
            except:
                va_offset=0

            """
            annotate_va的模式：
            'center'	垂直居中	文字的中线对齐锚点
            'top'	顶部对齐	文字的顶部对齐锚点
            'bottom'	底部对齐	文字的底部对齐锚点
            'baseline'	基线对齐	文字的基线对齐锚点（默认值）
            'center_baseline'	基线居中	文字的基线居中对齐锚点
            """
            
            #是否为终点文字加边框
            if annotate_bbox:
                ann=ax.annotate(text=ann_text, 
                             xy=(x_end, y_end),
                             xytext=(x_end, y_end + va_offset),
                             va=annotate_va,            # 垂直居中
                             ha=annotate_ha,              # （折线）水平靠左
                             textcoords="data",
                             arrowprops=dict(arrowstyle="->", color=last_line_color, lw=1.2, alpha=0.6),                        
                             color=last_line_color,
                             fontsize=annotate_txt_size,
                             #bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5),
                             bbox=dict(boxstyle="round,pad=0.3", fc=bbox_color, alpha=1.0),
                             )  
                # 分别提升 box 和文字的层级，遮盖先前绘制的内容
                ann.get_bbox_patch().set_zorder(10)  # box 在上
                ann.set_zorder(11)                   # 文字在 box 上
            else:
                if va_offset == 0:
                    ax.annotate(text=ann_text, 
                                 xy=(x_end, y_end),
                                 xytext=(x_end, y_end),
                                 va=annotate_va,            # 默认垂直居中
                                 ha=annotate_ha,              # 默认（折线）水平靠左
                                 #textcoords="data",
                                 #arrowprops=dict(arrowstyle="->", color=last_line_color, lw=1.2, alpha=0.6),                        
                                 color=last_line_color,
                                 fontsize=annotate_txt_size,
                                 )        
                else: 
                    ax.annotate(text=ann_text, 
                                 xy=(x_end, y_end),
                                 xytext=(x_end, y_end + va_offset),
                                 va=annotate_va,            # 垂直居中
                                 ha=annotate_ha,              # （折线）水平靠左
                                 textcoords="data",
                                 arrowprops=dict(arrowstyle="->", color=last_line_color, lw=1.2, alpha=0.6),                        
                                 color=last_line_color,
                                 fontsize=annotate_txt_size,
                                 )        
                
        #判断是否绘制关注线
        lmax=df1[l].max(); lmin=df1[l].min()
        
        for al in attention_values:
            pos=attention_values.index(al)
            
            line_al=False
            if (lmax >= al) and (al >= lmin): 
                line_al=True
            
            #如果需要绘制关注线，且尚未绘制过，则绘制
            if line_al and not attention_draws[pos]:
                ax.axhline(y=attention_values[pos],ls='dotted',c=color_list[pos],linewidth=1)

                attention_draws[pos]=True
        
    if technical1 in tech_close_same_list:
        #ylabeltxt1=ectranslate(indicator)
        ylabeltxt1=text_lang("价格","Price")
    else:
        ylabeltxt1=tech_list[technical1]+text_lang('指标',' indicators ')
    
    if mag_label != '':
        ylabeltxt1=ylabeltxt1+'('+mag_label+')'
    ax.set_ylabel(ylabeltxt1,fontsize=ylabel_txt_size)
    
    #对图例项目排序
    ax.legend(loc=loc1,fontsize=legend_txt_size)
    
    interval=int(len(df1)/10)+1
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))  # 隔interval天一个标记
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    titletxt1=text_lang("证券价格走势(德宏图)","Security Price Trend (Dehong Diagram)")
    titletxt=titletxt1+': '+ticker_name(ticker)+', '+tech_list[technical1]
    ax.set_title(titletxt+'\n',fontweight='bold',fontsize=title_txt_size)

    #绘制：收盘价，不同颜色和大小的marker-----------------------------------------
    #如果技术分析指标与价格是同一数量级，则使用单纵轴（避免图示变形），否则使用双纵轴
    ylabeltxt2=ectranslate(indicator)
    if technical1 in tech_close_same_list:
        #单纵轴
        ax2=ax
        loc2=loc1
    else:
        ax2 = ax.twinx()
        ax2.set_ylabel(ylabeltxt2,fontsize=ylabel_txt_size)
    
    #当日收盘价折线颜色
    price_line_color1=price_line_color[0]
    price_line_color2=price_line_color[1]

    #确定marker形状和lable
    price_line_marker1=price_line_marker[0]; labeltxt1=text_lang('当日↑','Bullish day')
    price_line_marker2=price_line_marker[1]; labeltxt2=text_lang('当日↓','Bearish day')

    #绘制价格折线
    ax2.plot(df1.index,df1[indicator],label=ylabeltxt2, \
             linestyle='solid',color='black',lw=price_line_width,alpha=0.5)   

    #绘制端点符号
    df1mk=df1[df1['marker_size'] > 0]
    
    #绘制上涨端点符号
    df1mkx=df1mk[df1mk['up_down'] > 0]
    pl_color=price_line_color1; pl_marker=price_line_marker1; labeltxt=labeltxt1
    #如果有端点可绘制
    if len(df1mkx) > 0:
        df1mk_tmp=df1mkx[df1mkx['marker_size'] == big_size]
        ax2.scatter(df1mk_tmp.index,df1mk_tmp[indicator],alpha=0.5, \
                    s=df1mk_tmp['marker_size'],lw=price_line_width, \
                    label=labeltxt,color=pl_color,marker=pl_marker)   

        df1mk_tmp=df1mkx[df1mkx['marker_size'] == mid_size]
        if len(df1mk_tmp) > 0:
            ax2.scatter(df1mk_tmp.index,df1mk_tmp[indicator],alpha=0.5, \
                        s=df1mk_tmp['marker_size'],lw=price_line_width, \
                        color=pl_color,marker=pl_marker)   

        df1mk_tmp=df1mkx[df1mkx['marker_size'] == small_size]
        if len(df1mk_tmp) > 0:
            ax2.scatter(df1mk_tmp.index,df1mk_tmp[indicator],alpha=0.5, \
                        s=df1mk_tmp['marker_size'],lw=price_line_width, \
                        color=pl_color,marker=pl_marker)   
    
    #绘制下跌端点符号
    df1mkx=df1mk[df1mk['up_down'] < 0]
    pl_color=price_line_color2; pl_marker=price_line_marker2; labeltxt=labeltxt2
    #如果有端点可绘制
    if len(df1mkx) > 0:
        df1mk_tmp=df1mkx[df1mkx['marker_size'] == big_size]
        ax2.scatter(df1mk_tmp.index,df1mk_tmp[indicator],alpha=0.5, \
                    s=df1mk_tmp['marker_size'],lw=price_line_width, \
                    label=labeltxt,color=pl_color,marker=pl_marker)   

        df1mk_tmp=df1mkx[df1mkx['marker_size'] == mid_size]
        if len(df1mk_tmp) > 0:
            ax2.scatter(df1mk_tmp.index,df1mk_tmp[indicator],alpha=0.5, \
                        s=df1mk_tmp['marker_size'],lw=price_line_width, \
                        color=pl_color,marker=pl_marker)   

        df1mk_tmp=df1mkx[df1mkx['marker_size'] == small_size]
        if len(df1mk_tmp) > 0:
            ax2.scatter(df1mk_tmp.index,df1mk_tmp[indicator],alpha=0.5, \
                        s=df1mk_tmp['marker_size'],lw=price_line_width, \
                        color=pl_color,marker=pl_marker)   
        
           
    """
    df1['segment'] = (np.sign(df1['up_down'].shift(1)) != np.sign(df1['up_down'])).cumsum()
    seg_list=list(set(list(df1['segment'])))

    #不同颜色/marker绘制涨跌价格线
    first_time=True; second_time=False
    for seg in seg_list:
        df1seg=df1[df1['segment']==seg]
        if df1seg['up_down'].values[0] >=0:
            seg_color=price_line_color1
            seg_marker=price_line_marker1
            #labeltxt=ylabeltxt2+'(当日↑)'
            #labeltxt=ylabeltxt2+'(当日阳线)'
            labeltxt=text_lang('当日↑','Bullish day')
        else:
            seg_color=price_line_color2
            seg_marker=price_line_marker2
            #labeltxt=ylabeltxt2+'(当日↓)'
            #labeltxt=ylabeltxt2+'(当日阴线)'
            labeltxt=text_lang('当日↓','Bearish day')
        #绘制涨跌三角标记
        df1seg_plot=df1seg[df1seg['marker_size'] > 0]
        if len(df1seg_plot) > 0:
            df1seg_tmp=df1seg_plot[df1seg_plot['marker_size'] == big_size]
            ax2.scatter(df1seg_tmp.index,df1seg_tmp[indicator], \
                        s=df1seg_tmp['marker_size'], \
                        label=labeltxt, \
                        color=seg_color,lw=price_line_width,marker=seg_marker,alpha=0.5)   

            df1seg_tmp=df1seg_plot[df1seg_plot['marker_size'] == mid_size]
            if len(df1seg_tmp) > 0:
                ax2.scatter(df1seg_tmp.index,df1seg_tmp[indicator], \
                            s=df1seg_tmp['marker_size'], \
                            #label=labeltxt, \
                            color=seg_color,lw=price_line_width,marker=seg_marker,alpha=0.5)   

            df1seg_tmp=df1seg_plot[df1seg_plot['marker_size'] == small_size]
            if len(df1seg_tmp) > 0:
                ax2.scatter(df1seg_tmp.index,df1seg_tmp[indicator], \
                            s=df1seg_tmp['marker_size'], \
                            #label=labeltxt, \
                            color=seg_color,lw=price_line_width,marker=seg_marker,alpha=0.5)   
    """
    #ax2.legend(loc=loc2,fontsize=legend_txt_size)
    #图例去重
    handles, labels = ax2.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # 去除重复项
    ax2.legend(by_label.values(), by_label.keys(), loc=loc2, fontsize=legend_txt_size)
    
    #绘制：交易量柱状图----------------------------------------------------------
    #区分涨跌颜色：假设红涨绿跌，可在参数中重定义
    if show_volume:
        df1up=df1[df1['up_down'] >= 0]
        df1down=df1[df1['up_down'] < 0]
    
        ax3 = fig.add_subplot(gs[1], sharex=ax)
        try:
            ax3.set_facecolor(facecolor2)
        except:
            ax3.set_facecolor('papayawhip')
    
        ax3.bar(df1up.index,df1up['Volume'],color=price_line_color1)
        ax3.bar(df1down.index,df1down['Volume'],color=price_line_color2)
        
        ax3.set_ylabel(text_lang("交易量(百万股)","Volume (in millions)"),fontsize=ylabel_txt_size -4)
    
    footnote1=text_lang("\n注：","\nNote: ")
    if (small_size > 0) or (mid_size > 0) or (big_size > 0):
        footnote2=text_lang("价格曲线的端点符号大小分别对应当日涨跌幅度的高低情形，","Node size describes price change amplitude. ")
    else:
        footnote2=''
    footnote3=text_lang("横轴日期上的空白处为非交易日\n","The blank areas of bars are non-trading days\n")
    
    import datetime; todaydt = str(datetime.date.today())
    footnote4=text_lang("数据来源：综合新浪/Stooq/Yahoo等，","Data source: Sina/Stooq/Yahoo, ")+todaydt
    
    footnote=footnote1+footnote2+footnote3+footnote4
    if show_volume:
        ax3.set_xlabel('\n'+footnote,fontsize=ylabel_txt_size -2)
    else:
        plt.xlabel('\n'+footnote,fontsize=ylabel_txt_size -2)
    
    #fig.text(0.5, 0.04, 'x', ha='center')
    plt.subplots_adjust(hspace=0.2)
    
    plt.gcf().autofmt_xdate()
    
    plt.gcf().set_facecolor(canvascolor) # 设置整个画布的背景颜色
    plt.show(); plt.close()
    
    return df1


#==============================================================================


def safe_annotate(ax, text, xy, xytext=(5, 5), color='black', fontsize=9, **kwargs):
    """
    在 ax 上添加注释，保证文字不会超出右边界。
    
    参数：
    - ax: matplotlib Axes 对象
    - text: 注释文字
    - xy: 注释点 (x, y)
    - xytext: 偏移量 (默认 (5,5))
    - kwargs: 传递给 annotate 的其他参数
    
    注意：函数单独测试似乎无问题，但嵌入程序中调用时出现奇怪错误，未启用！
    """
    ann = ax.annotate(text, xy=xy, xytext=xytext,
                      textcoords="offset points", ha="left", color=color, fontsize=fontsize, **kwargs)
    
    # 先绘制一次，才能拿到文字的 bbox
    ax.figure.canvas.draw()
    renderer = ax.figure.canvas.get_renderer()
    bbox = ann.get_window_extent(renderer=renderer)
    
    # 获取绘图区右边界
    ax_right = ax.get_window_extent().xmax
    
    # 如果文字超出右边界，就改成右对齐
    if bbox.xmax > ax_right:
        ann.set_ha("right")
    
    return ann

if __name__ =="__main__":
    # 🔹 使用示例
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    
    # 在右上角加注释
    safe_annotate(ax, "说明文字很长很长很长", xy=(1, 1))
    
    plt.show()


#==============================================================================
#==============================================================================
#==============================================================================


