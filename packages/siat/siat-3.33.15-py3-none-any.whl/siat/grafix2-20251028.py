# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
本模块功能：多点标记折线图，绘制动态折线图
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年10月17日
最新修订日期：2025年10月17日
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

#==============================================================================
import pandas as pd
import numpy as np

import matplotlib.dates as mdates

#==============================================================================
import matplotlib.pyplot as plt

import plotly.graph_objects as go
#==============================================================================

#设置刻度线风格：in，out，inout
plt.rcParams['xtick.direction'] = 'inout'  # 将x轴的刻度线方向设置向内
plt.rcParams['ytick.direction'] = 'inout'  # 将y轴的刻度方向设置向内内

#统一设定绘制的图片大小：数值为英寸，1英寸=100像素
plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

plt.rcParams['figure.facecolor']='whitesmoke' #背景颜色

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

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=False

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    #设置中文字体
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
#==============================================================================
#==============================================================================
#==============================================================================
if __name__ == "__main__":
    df=security_trend("000001.SS",start="MRY",graph=False)
    
    colname='Close'
    order=5; threshold=0.02
    
    highs_df, lows_df=find_major_turning_points_copilot(df, colname)

from scipy.signal import argrelextrema

def find_major_turning_points_copilot(df, colname, order=10):
    """
    在时间序列中寻找主要拐点（牛市顶和熊市底）。检测准确度有限！

    参数说明
    ----------
    df : pandas.DataFrame
        包含股价数据的 DataFrame，索引为日期。
    colname : str
        需要分析的价格列名。
    order : int, 默认 5
        局部极值检测的窗口大小（越大越严格）。
    threshold : float, 默认 0.02，暂不使用！
        涨跌幅阈值（相对前一拐点的幅度），小于该值的拐点会被忽略。越高越严格

    返回
    ----------
    turning_points : pandas.DataFrame
        包含主要拐点的 DataFrame，列包括：
        - 'date' : datetime，拐点日期
        - colname : float，拐点价格
        - 'type' : str，'peak' 或 'trough'
        - 'amplitude' : float，相对前一拐点的涨跌幅
    params : dict
        使用的参数字典 {'order': ..., 'threshold': ...}
    """

    try:
        series = df[colname]
    except:
        #对于某些指标，此时df的列名已经转换过，不再是colname
        colname_new=list(df)[0]
        series = df[colname_new]

    # 找局部极大值和极小值
    local_max_idx = argrelextrema(series.values, np.greater_equal, order=order)[0]
    local_min_idx = argrelextrema(series.values, np.less_equal, order=order)[0]

    peaks = pd.DataFrame({
        "Date": series.index[local_max_idx],
        colname: series.iloc[local_max_idx].values,
        "Type": "peak"
    })

    troughs = pd.DataFrame({
        "Date": series.index[local_min_idx],
        colname: series.iloc[local_min_idx].values,
        "Type": "trough"
    })

    turning_points = pd.concat([peaks, troughs]).sort_values("Date").reset_index(drop=True)

    # 计算涨跌幅
    turning_points["amplitude"] = turning_points[colname].pct_change()
    turning_points["amplitude_abs"] = turning_points["amplitude"].abs()

    # 按涨跌幅度绝对值降序排序
    turning_points.sort_values(by=["amplitude_abs"], ascending=False, inplace=True)
    turning_points.reset_index(drop=True,inplace=True)
    del turning_points["amplitude_abs"]
    
    highs_df=turning_points[turning_points['Type']=='peak']
    lows_df=turning_points[turning_points['Type']=='trough']
    
    return highs_df, lows_df



#==============================================================================
if __name__ == "__main__":
    df=security_trend("000001.SS",start="MRY",graph=False)
    
    colname='Close'
    
    highs_df, lows_df=find_major_turning_points_gemini(df, colname)

from scipy.signal import find_peaks

def find_major_turning_points_gemini(df: pd.DataFrame, colname: str) -> pd.DataFrame:
    """
    在时间序列数据中查找最突出的N个拐点（高点和低点）。
    
    参数:
    - df (pd.DataFrame): 输入的数据帧，必须包含一个日期时间类型的索引。
    - colname (str): df 中用于查找拐点的列名。

    返回:
    - pd.DataFrame: 一个最突出拐点信息的数据帧，
                    包含拐点日期'Date'、colname和'Type'('peak' 或 'trough')列。
    """
    df.index.name='Date'
    
    try:
        series = df[colname]
    except:
        #对于某些指标，此时df的列名已经转换过，不再是colname
        colname_new=list(df)[0]
        series = df[colname_new]

    # --- 1. 查找所有高点和低点及其“突出程度” ---
    # `prominence` 是衡量一个峰值/谷值相对于周围地形“突出”程度的指标，非常适合我们的需求。
    
    # 查找高点 (peaks)
    # prominence=(None, None) 表示计算所有找到的峰值的突出程度
    high_indices, high_props = find_peaks(series, prominence=(None, None))
    
    # 查找低点 (troughs) - 通过反转序列来查找峰值
    low_indices, low_props = find_peaks(-series, prominence=(None, None))

    # --- 2. 将高点和低点合并并计算排名 ---
    # 为高点创建 DataFrame
    highs_df = pd.DataFrame({
        'index_pos': high_indices,
        colname: series.iloc[high_indices].values,
        'Type': 'peak',
        'prominence': high_props['prominences']
    })
    
    # 为低点创建 DataFrame
    lows_df = pd.DataFrame({
        'index_pos': low_indices,
        colname: series.iloc[low_indices].values,
        'Type': 'trough',
        'prominence': low_props['prominences']
    })
    
    # 合并所有拐点
    all_points = pd.concat([highs_df, lows_df], ignore_index=True)
    
    # --- 3. 筛选出最突出的拐点 ---
    # 按“突出程度”降序排列
    top_points = all_points.sort_values(by='prominence', ascending=False)

    # --- 4. 格式化输出 ---
    # 使用原始的日期时间索引
    turning_points = top_points.copy()
    turning_points.index = df.index[turning_points['index_pos']]
    turning_points.reset_index(inplace=True)
    
    # 清理并排序最终的 DataFrame
    turning_points = turning_points[['Date', colname, 'Type', 'prominence']]
    
    highs_df=turning_points[turning_points['Type']=='peak']
    lows_df=turning_points[turning_points['Type']=='trough']
    
    return highs_df, lows_df

#==============================================================================
if __name__ == "__main__":
    df=security_trend("000001.SS",start="MRY",graph=False)
    
    colname='Close'
    
    highs_df, lows_df=find_major_turning_points_gemini(df, colname)
    
    rank_peak=5; rank_trough=5
    offset_pts=6
    x_rotation=30
    titletxt=None; xlabeltxt=None; ylabeltxt=None
    loc='best'
    facecolor='papayawhip'
    canvascolor='whitesmoke'
    
    plot_turning_points(df, colname, highs_df, lows_df, 
                            rank_peak=7,rank_trough=4)

def plot_turning_points(df, colname, highs_df, lows_df, 
                        rank_peak=5,rank_trough=5, 
                        attention_value=0,
                        offset_pts=15, 
                        x_rotation=30, 
                        
                        titletxt=None,xlabeltxt=None,ylabeltxt=None,
                        loc='best',
                        
                        facecolor='papayawhip',
                        canvascolor='whitesmoke',
                        ):
    """
    在时间序列曲线上标注主要拐点，并额外标注期间最高点和最低点。
    可用于股价、成交量、收益率、波动率等任意数值型指标。单个指标！！！

    参数说明
    ----------
    df : pandas.DataFrame
        包含时间序列数据的 DataFrame，索引为日期。
    colname : str
        需要绘制的列名（如 "Close"、"Volume"、"Ret%"、"Volatility"）。
    highs_df, lows_df : pandas.DataFrame
        拐点信息，至少包含以下列：
        - 'Date' : datetime，拐点日期
        - colname : float，拐点数值
        - 'Type' : str，'peak' 或 'trough'

    rank_peak, rank_trough : int, 默认 5
        标注的高低拐点数量。

    offset_pts : int, 默认 6
        标注文字的纵向偏移量（点数，避免文字与曲线重叠）。
    x_rotation : int, 默认 30
        横轴日期标签的旋转角度。

    返回
    ----------
    None
        直接绘制并显示图表。
    """
    try:
        series = df[colname]
    except:
        #对于某些指标，此时df的列名已经转换过，不再是colname
        colname_new=list(df)[0]
        series = df[colname_new]

    fig, ax = plt.subplots()
    fig.patch.set_facecolor(canvascolor)   # 设置整张图的背景色
    
    colnametxt=ectranslate(colname)
    #ax.plot(df.index, df[colname], label=colnametxt, color="black", lw=1.5)
    ax.plot(df.index, series, label=colnametxt, color="black", lw=1.5)
    
    if isinstance(attention_value,list):
        # 这里仅仅支持单值
        attention_value=attention_value[0]
    cross_value=is_cross_value(df,colname,attention_value)
    if cross_value:
        ax.axhline(y=attention_value, color='lightgrey', linestyle='dotted', linewidth=2)
    
    # 选出需要绘制的高点低点
    peaks=highs_df.head(rank_peak)
    troughs=lows_df.head(rank_trough)
        
    # 期间最高点和最低点
    #max_idx = df[colname].idxmax()
    max_idx = series.idxmax()
    #min_idx = df[colname].idxmin()
    min_idx = series.idxmin()
    
    max_point = {"Date": max_idx, colname: series.loc[max_idx], "Type": "max"}
    min_point = {"Date": min_idx, colname: series.loc[min_idx], "Type": "min"}
    
    if max_idx in peaks['Date'].values:
        max_point = None
    if min_idx in troughs['Date'].values:
        min_point = None

    # 绘制点
    peaktxt=text_lang("高拐点","Peak")
    troughtxt=text_lang("低拐点","Trough")
    periodHtxt=text_lang("期间最高点","Period High")
    periodLtxt=text_lang("期间最低点","Period Low")
    
    ax.scatter(peaks['Date'], peaks[colname], color="red", marker="^", s=90, label=peaktxt, zorder=3)
    ax.scatter(troughs['Date'], troughs[colname], color="green", marker="v", s=90, label=troughtxt, zorder=3)
    if max_point:
        ax.scatter(max_point["Date"], max_point[colname], color="darkred", marker="*", s=140, label=periodHtxt, zorder=4)
    if min_point:
        ax.scatter(min_point["Date"], min_point[colname], color="darkgreen", marker="*", s=140, label=periodLtxt, zorder=4)

    def annotate_points(points, color, vertical_offset, sign):
        for row in points:
            if row is None:
                continue
            date, value = row['Date'], row[colname]
            #label = f"{date.strftime('%m-%d')}\n{value:.2f}"
            label = f"{date.strftime('%Y-%m-%d')}\n{srounds(value)}"

            ax.annotate(
                label,
                xy=(date, value),
                xytext=(0, vertical_offset),   # 只上下偏移
                textcoords="offset points",
                ha="center", 
                va="bottom" if sign=="+" else "top",
                color=color, fontsize=9,
                bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", pad=0.5),
                zorder=5
            )

    # 标注牛市顶（在上方）
    annotate_points(peaks.to_dict("records"), "red", offset_pts, "+")
    # 标注熊市底（在下方）
    annotate_points(troughs.to_dict("records"), "green", -offset_pts, "-")
    # 标注全局最高/最低
    if max_point:
        annotate_points([max_point], "darkred", offset_pts, "+")
    if min_point:
        annotate_points([min_point], "darkgreen", -offset_pts, "-")

    if titletxt is None:
        titletxt=f"Security Trend: Indicator {colname} with Major Turning Points"
    ax.set_title(titletxt+'\n',fontsize=title_txt_size)
    
    if xlabeltxt is None:
        xlabeltxt="Date"
    ax.set_xlabel('\n'+xlabeltxt,fontsize=xlabel_txt_size,ha='center')
    
    if ylabeltxt is None:
        ylabeltxt=colname
    ax.set_ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    
    ax.legend(loc=loc,fontsize=legend_txt_size)
    
    ax.set_facecolor(facecolor)   # 设置绘图区背景色
    
    #ax.grid(True, alpha=0.3)

    # 自动选择横轴日期粒度
    span_days = (series.index.max() - series.index.min()).days
    if span_days < 90:
        locator = mdates.DayLocator(interval=7)
        formatter = mdates.DateFormatter("%m-%d")
    elif span_days < 730:
        locator = mdates.MonthLocator(interval=1)
        formatter = mdates.DateFormatter("%Y-%m")
    else:
        locator = mdates.YearLocator()
        formatter = mdates.DateFormatter("%Y")

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    fig.autofmt_xdate(rotation=x_rotation)

    plt.tight_layout()
    plt.show(); plt.close()

#==============================================================================
if __name__=='__main__':
    colnames="Close"
    colnames="beta"
    
    df=security_trend("600519.SS",start="MRY",indicator=colnames,graph=False)
    
    df=security_trend(["000001.SS","000300.SS"],start="MRY",graph=False)
    
    df=security_trend("600519.SS",indicator=["Close","Adj Close"],start="MRY",graph=False)
    
    attention_value=0
    
    width=1000; height=600
    titletxt=xlabeltxt=ylabeltxt=None
    title_distance=0.95
    title_font=None
    
    
def plot_dynamic_plotly(df, colnames, width=1000, height=600, 
                        attention_value=0,
                        titletxt=None,
                        #title_distance=0.98,
                        title_font=None,
                        xlabeltxt=None, ylabeltxt=None,
                        facecolor='papayawhip',canvascolor='whitesmoke',
                        ):
    """
    使用 Plotly 绘制交互式折线图。
    - 自动根据时间跨度设置横轴刻度
    - 多列时使用不同颜色和线型区分，最多支持 7 列
    - 支持自定义标题距离和字体
    """
    
    #判断df的字段是否与colnames一致
    df_cols=list(df)
    if isinstance(colnames, str):
        if colnames in df_cols:
            colnames_new = [colnames]
        else:
            colnames_new = df_cols
    else:
        colnames_new = colnames

    # 最多支持 7 种线型
    linestyles = ["solid", "dotted", "dashdot", "dashed", "longdash", "longdashdot", "dashdot"]
    
    # Plotly 默认会自动分配醒目的颜色，这里只需要循环线型
    fig = go.Figure()

    #模式x unified与x的区别：集成各个曲线的文字在一个框中显示，还集成横轴的日期标签，并跟随其格式
    hovermodetxt="x unified"
    
    for i, col in enumerate(colnames_new[:7]):  # 限制最多 7 列
        formatted = df[col].apply(srounds) #折线数据小数点格式化
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode="lines+markers", 
            marker=dict(size=2.5), #端点如果太大，样本密集时折线不好看
            name=ectranslate(col),
            line=dict(dash=linestyles[i % len(linestyles)], width=2),
            text=formatted,  # 这里传入格式化后的数值字符串
            #这里去掉了每条折线各自的日期标签
            hovertemplate=f"{ectranslate(col)}: %{{text}}<extra></extra>"
        ))

    #判断是否需要绘制水平关注线
    cross_value=is_cross_value(df,colnames_new,attention_value)
    if cross_value:
        # 添加水平虚线
        fig.add_hline(
            y=attention_value,  # 水平线的y值
            line=dict(
                dash="dot",  # 虚线类型
                color="lightgrey",  # 颜色
                width=3,       # 线宽（像素）
            ),
        )        

    if titletxt is None:
        titletxt="Security Trend: Interactive Indicator(s)"
    if xlabeltxt is None:
        xlabeltxt="Date"
    if ylabeltxt is None:
        if len(colnames_new) == 1:
            ylabeltxt=colnames_new[0]
        else:
            ylabeltxt="Value"

    fig.update_layout(
        title=dict(
            text=titletxt,
            #pad=dict(t=0,b=20),  # 标题顶部与自身容器上边缘的间距
            x=0.5,
            xanchor="center",
            yanchor='top',   # 将标题的 *顶部* 锚定在 0.98 的位置
            y=0.98, ## 将标题设置在画布 98% 的高度（1.0 可能会被裁切）
            font=title_font if title_font else dict(size=title_txt_size, color="black")
        ),
        width=width,
        height=height,
        
        #xaxis_title='\n'+xlabeltxt,
        xaxis=dict(title=dict(text='\n'+xlabeltxt,font=dict(size=xlabel_txt_size))),
        
        #yaxis_title=ylabeltxt,
        yaxis=dict(title=dict(text=ylabeltxt,font=dict(size=ylabel_txt_size))),
        
        #hovermode="x unified",
        #hovermode="x",
        hovermode=hovermodetxt,
        template="plotly_white",
        
        plot_bgcolor=facecolor,
        paper_bgcolor=canvascolor,
        
        #控制整个图形区域（包括标题和图表内容）与画布顶部外边框的距离
        #即图形区域上边缘到画布边框的间距，像素点数
        margin=dict(t=60), # 设置 *图形区域* 距离画布顶部 60 像素
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1,
                    font=dict(size=legend_txt_size)),
    )

    # 中文：设置横轴日期格式 + 倾斜角度
    lang=check_language()
    if lang == "Chinese":
        fig.update_xaxes(
            tickformat="%Y-%m-%d", #格式化横轴日期显示格式
            tickangle=-30   # 刻度文字顺时针倾斜30度
        )
    
    fig.show()
    
    
#==============================================================================
if __name__=='__main__':
    df,found=get_price_1ticker_mixed(ticker='600519.SS',fromdate='2025-6-1', \
                              todate='2025-10-20')
    draw_candlestick(df,
                 pricename={'open':'Open','high':'High','low':'Low','close':'Close'},
                 volumename='Volume')
    
    pricename={'open':'Open','high':'High','low':'Low','close':'Close'}
    volumename='Volume'
    

def draw_candlestick(df, pricename, volumename,
                     mav=[5,10],
                     barcolor=['red','green'],
                     titletxt='K-Line',
                     ylabeltxt=['Price','Volume'],
                     xlabeltxt='Data source: Sina Finance',
                     facecolor='papayawhip',
                     canvascolor='whitesmoke',
                     loc='best'):
    """
    绘制K线图 + 成交量柱状图 + 均线 + 成交量趋势线
    df: DataFrame，索引为日期（升序）
    pricename: dict，包含 'open','high','low','close' 四个字段名
    volumename: str，成交量字段名
    """

    # 设置画布
    fig, (ax_price, ax_vol) = plt.subplots(
        2, 1, figsize=(12,8), sharex=True,
        gridspec_kw={'height_ratios':[3,1]}
    )
    fig.patch.set_facecolor(canvascolor)
    ax_price.set_facecolor(facecolor)
    ax_vol.set_facecolor(facecolor)

    # 日期转为数字索引
    dates = mdates.date2num(df.index.to_pydatetime())
    opens = df[pricename['open']].values
    highs = df[pricename['high']].values
    lows = df[pricename['low']].values
    closes = df[pricename['close']].values
    volumes = df[volumename].values

    width = 0.6  # K线实体宽度

    # 绘制K线
    for i in range(len(df)):
        if closes[i] >= opens[i]:  # 阳线
            color = barcolor[0]
            lower = opens[i]
            height = closes[i] - opens[i]
        else:  # 阴线
            color = barcolor[1]
            lower = closes[i]
            height = opens[i] - closes[i]

        # 实体
        ax_price.add_patch(
            plt.Rectangle((dates[i]-width/2, lower), width, height,
                          facecolor=color, edgecolor=color)
        )
        # 上下影线
        ax_price.vlines(dates[i], lows[i], highs[i], color=color, linewidth=1)

    # 绘制价格均线
    linestyles = ['-','--','-.',':']
    colors = ['blue','orange','purple','brown']
    for i, ma in enumerate(mav[:4]):
        df[f'MA{ma}'] = df[pricename['close']].rolling(ma).mean()
        ax_price.plot(dates, df[f'MA{ma}'], 
                      linestyle=linestyles[i%len(linestyles)],
                      color=colors[i%len(colors)],
                      label=f'MA{ma}')

    # 绘制成交量柱状图
    vol_colors = [barcolor[0] if closes[i]>=opens[i] else barcolor[1] for i in range(len(df))]
    ax_vol.bar(dates, volumes, color=vol_colors, width=0.6, align='center')
    # 成交量折线
    #ax_vol.plot(dates, volumes, color='black', linewidth=1, alpha=0.7, label='Volume')

    # 设置标题和标签
    ax_price.set_title(titletxt, fontsize=title_txt_size)
    ax_price.set_ylabel(ylabeltxt[0], fontsize=ylabel_txt_size)
    ax_vol.set_ylabel(ylabeltxt[1], fontsize=ylabel_txt_size)
    ax_vol.set_xlabel(xlabeltxt, fontsize=xlabel_txt_size)

    # 日期格式化：尽可能多显示，并包含首尾日期
    locator = mdates.AutoDateLocator(minticks=10, maxticks=20)
    ax_vol.xaxis.set_major_locator(locator)
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # 强制横轴范围覆盖首尾日期
    ax_vol.set_xlim(dates[0], dates[-1])

    # 手动加上首尾刻度
    xticks = list(ax_vol.get_xticks())
    xticks.extend([dates[0], dates[-1]])
    ax_vol.set_xticks(sorted(set(xticks)))

    plt.setp(ax_vol.get_xticklabels(), rotation=30, ha='right')
    #plt.setp(ax_vol.get_xticklabels(), rotation=30, ha='center')

    # 图例
    ax_price.legend(loc=loc, fontsize=legend_txt_size)
    #ax_vol.legend(loc=loc, fontsize=)

    plt.tight_layout()
    plt.show()
    
    
#==============================================================================
if __name__=='__main__':
    df,found=get_price_1ticker_mixed(ticker=['600519.SS','000858.SZ'],
                              fromdate='2025-6-1', \
                              todate='2025-10-24')
    
    method='pearson'
    window=252
    offset=None
    offset_range=None
    attention_value=None
    attention_point='2025-10-20'
    
    titletxt=None
    ylabeltxt=None
    xlabeltxt=None
    facecolor='papayawhip'
    canvascolor='whitesmoke'
    printout=True
    
    plot_trend_correlation(df,attention_value=0.8,attention_point=attention_point)

from scipy import stats
from itertools import cycle

def plot_trend_correlation(
        df,
        method='pearson',
        window=252,
        offset=None,
        offset_range=None,
        attention_value=None,
        attention_point=None,
        titletxt=None,
        ylabeltxt=None,
        xlabeltxt=None,
        facecolor='papayawhip',
        canvascolor='whitesmoke',
        loc='best',
        printout=True,
    ):
    """
    绘制df的第1个字段与其余字段的滚动相关系数趋势折线，
    线型区分不同证券，线宽体现显著性强弱，自动搜索最优 offset。
    """
    print("  Processing correlation, it may take long time ...")
    
    df_cols=list(df)
    df_cols
    ticker1=df_cols[0]
    ticker2=df_cols[1:4]

    # ---------- 参数检查 ----------
    if offset is None:
        offset = [0] * len(ticker2)
    offset = list(offset)
    if len(offset) != len(ticker2):
        raise ValueError("  #Error: offset mismatches with comparees in length")

    # ---------- 计算滚动相关与 p 值 ----------
    def rolling_corr_and_p(x, y, window, method='pearson'):
        n = len(x)
        corr = np.full(n, np.nan)
        pval = np.full(n, np.nan)
        for i in range(window - 1, n):
            xa = x[i - window + 1:i + 1]
            ya = y[i - window + 1:i + 1]
            mask = np.isfinite(xa) & np.isfinite(ya)
            if mask.sum() < 3:
                continue
            try:
                if method == 'pearson':
                    r, p = stats.pearsonr(xa[mask], ya[mask])
                else:
                    r, p = stats.spearmanr(xa[mask], ya[mask])
                corr[i] = r if np.isfinite(r) else np.nan
                pval[i] = p if np.isfinite(p) else np.nan
            except Exception:
                continue
        return corr, pval

    # ---------- 自动优化 offset ----------
    
    if offset_range is None:
        offset_range=5
    search_range = range(-offset_range, offset_range)
    best_offsets = []

    print("  Optimizing offset for higher significance ...")
    for j, tkr in enumerate(ticker2):
        best_off = offset[j]
        best_metric = np.inf
        x = df[ticker1].values
        for off in search_range:
            y = df[tkr].shift(off).values
            _, pvals = rolling_corr_and_p(x, y, window, method)
            med = np.nanmedian(pvals)
            if np.isnan(med):
                continue
            if med < best_metric:
                best_metric = med
                best_off = off

            # 显示进度
            total_count=len(ticker2) * len(search_range)
            current=j * len(search_range) + search_range.index(off)
            print_progress_percent(current,total_count,steps=10,leading_blanks=4, finalizing=False)
        
        best_offsets.append(best_off)

    # ---------- 绘图 ----------
    fig, ax = plt.subplots(figsize=(12.8, 6.4), facecolor=canvascolor)
    ax.set_facecolor(facecolor)
    color_cycle = cycle(plt.cm.tab10.colors)
    linestyle_cycle = cycle(['-', '--', '-.', ':'])

    idx = df.index

    # 准备关注线列表
    if attention_value is None:
        attention_value=[0]
    elif isinstance(attention_value,float):
        attention_value=[attention_value]
    else:
        pass
        
    print("  Finetuning correlation curves ...")
    for tkr, off, color, ls in zip(ticker2, best_offsets, color_cycle, linestyle_cycle):
        x = df[ticker1].values
        y = df[tkr].shift(off).values
        corr, pval = rolling_corr_and_p(x, y, window, method)

        # 根据显著性调整线宽
        """
        lw_arr = np.where(np.isfinite(pval),
                          np.where(pval < 0.01, 3.5,
                                   np.where(pval < 0.05, 2.0,
                                            np.where(pval < 0.1, 1.5, 1.0))),
                          1.0)
        """
        lw_arr = np.where(np.isfinite(pval),
                          np.where(pval < 0.001, 5,
                              np.where(pval < 0.01, 3.5,
                                       np.where(pval < 0.05, 2.0,
                                                np.where(pval < 0.1, 1.5, 1.0)))),
                          1.0)
        
        
        # 直接绘制连续线（不用逐段）
        ax.plot(idx, corr, color=color, ls=ls, lw=1.0, alpha=0.8)

        # 用滚动显著性线宽叠加效果
        for i in range(1, len(idx)):
            if not (np.isfinite(corr[i - 1]) and np.isfinite(corr[i])):
                continue
            ax.plot(idx[i - 1:i + 1], corr[i - 1:i + 1],
                    color=color, 
                    lw=lw_arr[i],
                    ls=ls, 
                    alpha=0.9)
        
        # 绘制关注值
        for av in attention_value:
            result = is_cross_value_series(corr, av)
            if result:
                ax.axhline(av, color='k', lw=2, alpha=0.5, ls=':')

        # 标签
        if np.isfinite(corr[-1]):
            ax.text(idx[-1], corr[-1], f' {tkr} ({off:+d})',
                    color=color, va='center', fontsize=annotate_size)


    # ---------- 图形美化 ----------
    if titletxt is None:
        titletxt=f'Rolling {method.title()} Correlation ({window} Trading Days) vs {ticker1}'
    ax.set_title(titletxt+'\n', fontsize=title_txt_size)

    if xlabeltxt is None:
        xlabeltxt='Date'
    ax.set_xlabel('\n'+xlabeltxt, fontsize=xlabel_txt_size)

    if ylabeltxt is None:
        ylabeltxt='Correlation'
    ax.set_ylabel(ylabeltxt, fontsize=ylabel_txt_size)
        
    # 绘制关注日期
    legend_flag=False
    if not (attention_point is None):
        if isinstance(attention_point,str):
            attention_point=[attention_point]
            
        for ap in attention_point:
            """
            df_ap = df.loc[ap:ap]
            
            if len(df_ap) > 0:
            """
            legend_flag=True
            appd=pd.to_datetime(ap)
            ap_str=appd.strftime('%Y-%m-%d')
            ax.axvline(x=appd,ls=":",c='k',linewidth=2,alpha=0.5, \
                        label=text_lang("关注点","Attention point ")+ap_str)
 
    ax.grid(alpha=0.3)
        
    if legend_flag:
        plt.legend(loc=loc,fontsize=legend_txt_size)

    plt.tight_layout()
    plt.show()

    if printout:
        print("  Optimal offset:", dict(zip(ticker2, best_offsets)))
        
    return best_offsets

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================


