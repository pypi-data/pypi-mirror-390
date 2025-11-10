# -*- coding: utf-8 -*-
"""
本模块功能：RAR结果评估算法
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年11月2日
最新修订日期：2025年11月2日
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

#==============================================================================

import pandas as pd
import numpy as np
#==============================================================================
from siat.risk_adjusted_return2 import *
#==============================================================================
if __name__=='__main__':
    ticker=['300308.SZ', '300502.SZ', '000063.SZ', '600941.SS', '600050.SS']
    start='2023-10-31'; end='2025-10-31';mktidx='000001.SS'
    
    df,_=compare_mticker_1rar(ticker,start,end,rar='sharpe', \
                             ret_type="Annual Adj Ret%",RF=0, \
                             graph=False,printout=False, \
                             mktidx=mktidx,source='auto',ticker_type='auto')


#==============================================================================
if __name__=='__main__':
    
    result_copilot=rar_recommend_copilot(df,
            window_lengths = {"short": 63, "mid": 252, "long": 756})
    
def rar_recommend_copilot(
    df: pd.DataFrame,
    window_lengths: dict = None,
    profiles: dict = None,
    return_scores: bool = False,
    min_obs: int = 10,
    ) -> (pd.DataFrame, pd.DataFrame):
    """
    Build star recommendations (1–5 stars) for each stock across investor profiles and horizons
    based on ratio time series (Sharpe, Sortino, Treynor, Alpha). Index must be ascending dates.

    Parameters
    ----------
    df : pd.DataFrame
        Rows: dates (ascending). Columns: stocks. Values: ratio (can be Sharpe/Sortino/Treynor/Alpha).
    window_lengths : dict, optional
        Row-count windows per horizon. Defaults assume daily data:
        {"short": 63, "mid": 252, "long": 756}. Adjust to your frequency (e.g., monthly: 6/12/36).
    profiles : dict, optional
        Weight dicts over four components: level, trend, stability, consistency (sum to 1).
        Defaults:
            {
              "aggressive": {"level": 0.35, "trend": 0.35, "stability": 0.15, "consistency": 0.15},
              "balanced":  {"level": 0.30, "trend": 0.25, "stability": 0.25, "consistency": 0.20},
              "conservative":{"level": 0.20, "trend": 0.10, "stability": 0.40, "consistency": 0.30}
            }
    return_scores : bool, optional
        If True, also return a detailed score dataframe for audit/teaching.
    min_obs : int
        Minimal non-NaN observations required in a window to compute metrics.

    Returns
    -------
    stars_df : pd.DataFrame
        Index: stock. Columns: "<profile>_<horizon>" with star strings ("★" * n, max 5).
    scores_df : pd.DataFrame (optional if return_scores=True)
        MultiIndex columns: (horizon, component) for components plus (horizon, "<profile>_total")
        Numeric standardized component scores and weighted totals.
    """
    # Defaults
    if window_lengths is None:
        window_lengths = {"short": 21, "mid": 63, "long": 252}
    if profiles is None:
        profiles = {
            "aggressive":   {"level": 0.35, "trend": 0.35, "stability": 0.15, "consistency": 0.15},
            "balanced":     {"level": 0.30, "trend": 0.25, "stability": 0.25, "consistency": 0.20},
            "conservative": {"level": 0.20, "trend": 0.10, "stability": 0.40, "consistency": 0.30},
        }

    # Ensure ascending index and drop all-NaN columns robustly
    df = df.sort_index()
    stocks = df.columns

    # Helper: compute components for one horizon (last window)
    def components_for_window(window_df: pd.DataFrame):
        """
        Returns a DataFrame with raw component metrics per stock:
        level (mean), trend (slope), stability (inverse std), consistency (1 - share negative)
        """
        # Count valid obs
        valid_counts = window_df.notna().sum(axis=0)

        # Level: mean ratio
        level = window_df.mean(axis=0)

        # Trend: slope via simple OLS on index order (robust to irregular dates)
        # x as 0..(n-1) within each stock's valid observations
        trend_vals = []
        for col in window_df.columns:
            s = window_df[col].dropna()
            if len(s) < min_obs:
                trend_vals.append(np.nan)
                continue
            x = np.arange(len(s)).astype(float)
            x_mean = x.mean()
            y_mean = s.mean()
            # slope = cov(x,y)/var(x)
            denom = ((x - x_mean) ** 2).sum()
            slope = np.nan if denom == 0 else ((x - x_mean) * (s.values - y_mean)).sum() / denom
            trend_vals.append(slope)
        trend = pd.Series(trend_vals, index=window_df.columns)

        # Stability: inverse of std (higher = more stable). Use 1/(1+std) to bound.
        std = window_df.std(axis=0)
        stability = 1.0 / (1.0 + std)

        # Consistency: 1 - share of negatives (higher = fewer negative periods)
        neg_share = window_df.apply(lambda s: (s < 0).sum() / s.count() if s.count() > 0 else np.nan)
        consistency = 1.0 - neg_share

        raw = pd.DataFrame({
            "level": level,
            "trend": trend,
            "stability": stability,
            "consistency": consistency,
            "valid_n": valid_counts,
        })
        # Mask insufficient data
        raw.loc[raw["valid_n"] < min_obs, ["level", "trend", "stability", "consistency"]] = np.nan
        return raw

    # Component computation per horizon
    components = {}
    for horizon, w in window_lengths.items():
        # Take last w rows; if fewer rows exist, use all
        window_df = df.tail(w)
        raw = components_for_window(window_df)
        # Cross-sectional z-scores for components (higher is better across the board)
        z = raw[["level", "trend", "stability", "consistency"]].apply(
            lambda col: (col - col.mean(skipna=True)) / col.std(skipna=True), axis=0
        )
        components[horizon] = z

    # Weighted totals per profile and horizon
    totals = {}
    for horizon, z in components.items():
        for pname, wts in profiles.items():
            total = (
                z["level"]   * wts["level"] +
                z["trend"]   * wts["trend"] +
                z["stability"] * wts["stability"] +
                z["consistency"] * wts["consistency"]
            )
            totals[(pname, horizon)] = total

    totals_df = pd.DataFrame(totals)

    # Convert totals (per horizon) to stars via quantiles (relative ranking in cross-section)
    def to_stars(series: pd.Series) -> pd.Series:
        # Map NaN to 0 stars
        if series.notna().sum() == 0:
            return pd.Series([""] * len(series), index=series.index)
        ranks = series.rank(method="average", na_option="keep")
        pct = ranks / ranks.max()
        # Quantile cut points -> 1..5 stars
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0000001]
        labels = [1, 2, 3, 4, 5]
        stars = pd.cut(pct, bins=bins, labels=labels, include_lowest=True)
        # Create star strings
        star_str = stars.apply(lambda n: "★" * int(n) if pd.notna(n) else "")
        return star_str

    star_cols = {}
    for (pname, horizon), s in totals_df.items():
        star_cols[f"{pname}_{horizon}"] = to_stars(s)

    stars_df = pd.DataFrame(star_cols, index=stocks)

    # Optional: detailed score breakdown for transparency
    if return_scores:
        # Assemble components and totals into a tidy MultiIndex columns dataframe
        # Components
        comp_frames = []
        for horizon, z in components.items():
            c = z.copy()
            c.columns = pd.MultiIndex.from_product([[horizon], c.columns])
            comp_frames.append(c)
        scores_df = pd.concat(comp_frames, axis=1)

        # Totals
        tot_frames = []
        for (pname, horizon), s in totals_df.items():
            col = pd.MultiIndex.from_product([[horizon], [f"{pname}_total"]])
            tot_frames.append(pd.DataFrame(s.values, index=s.index, columns=col))
        totals_tidy = pd.concat(tot_frames, axis=1)

        scores_df = pd.concat([scores_df, totals_tidy], axis=1)
        # Order columns by horizon
        scores_df = scores_df.reindex(
            columns=pd.MultiIndex.from_product(
                [list(window_lengths.keys()),
                 ["level", "trend", "stability", "consistency",
                  "aggressive_total", "balanced_total", "conservative_total"]]
            ),
            fill_value=np.nan
        )
        return stars_df, scores_df

    return stars_df

"""
Design overview
核心思想: 在每个持有期窗口内，综合比率的平均水平、线性趋势斜率、波动稳定性、负值占比（一致性）四项，按不同风险偏好加权，得到相对评分并转换为1–5星。
窗口定义: 短期/中期/长期默认使用行数窗口（适应任意频率），可自定义。
相对性: 每个持有期内对所有股票做横截面标准化（z-score），避免量纲与频率差异。
透明性: 可选择返回详细评分（水平、趋势、稳定、一致性以及加权总分），用于审计。

Metric definitions and rationale
Level: 窗口内的平均比率，代表该阶段的“绝对表现水平”。越高越好。
Trend: 简单线性回归斜率（以序号为横轴），衡量近期动量与趋势强度。越高越好。
Stability: 1/(1+标准差)，把波动率映射到(0,1]范围，越稳定越接近1。
Consistency: 1 - 负值占比，强调“少踩雷”的一致性，越高越好。

Investor profiles and horizons
Aggressive: 强调水平与趋势，次重稳定与一致性。
Balanced: 四维均衡。
Conservative: 强调稳定与一致性，弱化趋势。
Horizons: 默认短/中/长期行数窗口为 63/252/756（适合日频）。若是月频，建议改为 6/12/36。可以把 window_lengths 设为适配频率的行数。

Practical tips
频率适配: 如果 df 是月频或周频，直接改 window_lengths 为行数即可，不依赖日期推断。
空缺与稳健性: 少于 min_obs 的窗口返回空星（空字符串），保持保守与透明。
课堂透明: 设 return_scores=True 可获得每个组件的 z-score 以及各画像的加权总分，便于讲解与审计。
可扩展性: 若需要把不同比率（如 Sharpe 与 Alpha）分列融合，可先标准化后加权合并，再喂给本函数。
"""
#==============================================================================
if __name__=='__main__':
    
    result_chatgpt=rar_recommend_chatgpt(df,
        short_window = 20,mid_window = 60,long_window = 252,
        )

from scipy.stats import linregress

def _slope_of_series(s: pd.Series) -> float:
    s = s.dropna()
    if len(s) < 2:
        return 0.0
    x = np.arange(len(s))
    res = linregress(x, s.values)
    return float(res.slope)

def _minmax_scaler(series: pd.Series) -> pd.Series:
    mn = series.min()
    mx = series.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)

def _stars_str(n: int) -> str:
    """把星级数字（0~5）转为仅含实心星 '★' 的字符串；0 -> ''（空字符串）。
    若想把 0 显示为 '-' 或 '无'，把 return 改为: return '-' if n==0 else '★'*n
    """
    n = int(np.clip(n, 0, 5))
    return "★" * n if n > 0 else ""

def rar_recommend_chatgpt(
    df: pd.DataFrame,
    short_window: int = 20,
    mid_window: int = 60,
    long_window: int = 252,
    slope_window: int | None = None,
    star_method: str = "scale",  # "scale" or "quantile"
    quantile_bins: int = 5
    ) -> pd.DataFrame:
    """
    输入:
      df: index 为时间（升序），columns 为股票，values 为夏普比率或类似指标。
    返回:
      DataFrame：每只股票若干星级列（仅实心星 '★'，0 星为空字符串）及中间原始指标。
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame")
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df = df.copy()
            df.index = pd.to_datetime(df.index)
        except Exception:
            raise ValueError("df index must be datetime-like or convertible to datetime")

    if not df.index.is_monotonic_increasing:
        df = df.sort_index()

    horizons = {"short": short_window, "mid": mid_window, "long": long_window}

    weights = {
        "Aggressive": {"mean": 0.35, "stability": 0.05, "slope": 0.30, "consistency": 0.05, "last": 0.25},
        "Balanced":   {"mean": 0.30, "stability": 0.20, "slope": 0.25, "consistency": 0.10, "last": 0.15},
        "Conservative":{"mean": 0.20, "stability": 0.40, "slope": 0.05, "consistency": 0.25, "last": 0.10}
    }

    stocks = df.columns.tolist()
    records = {}

    # 计算每个 horizon 的原始指标
    for hname, window in horizons.items():
        slope_w = slope_window or window
        metrics = {
            "mean": pd.Series(index=stocks, dtype=float),
            "std": pd.Series(index=stocks, dtype=float),
            "slope": pd.Series(index=stocks, dtype=float),
            "positive_ratio": pd.Series(index=stocks, dtype=float),
            "last": pd.Series(index=stocks, dtype=float)
        }

        last_slice = df.iloc[-window:] if window <= len(df) else df.copy()
        slope_slice = df.iloc[-slope_w:] if slope_w <= len(df) else df.copy()

        for stock in stocks:
            s = last_slice[stock].dropna()
            if len(s) == 0:
                metrics["mean"].loc[stock] = np.nan
                metrics["std"].loc[stock] = np.nan
                metrics["positive_ratio"].loc[stock] = np.nan
                metrics["last"].loc[stock] = np.nan
            else:
                metrics["mean"].loc[stock] = float(s.mean())
                metrics["std"].loc[stock] = float(s.std(ddof=0))
                metrics["positive_ratio"].loc[stock] = float((s > 0).mean())
                metrics["last"].loc[stock] = float(s.iloc[-1])
            # slope 计算（用 slope_slice）
            metrics["slope"].loc[stock] = _slope_of_series(slope_slice[stock])

        records[hname] = metrics

    # 标准化各指标（股票间）
    norm_store = {}
    for hname, metrics in records.items():
        df_metrics = pd.DataFrame(metrics)
        norm_df = pd.DataFrame(index=stocks)
        for col in ["mean", "std", "slope", "positive_ratio", "last"]:
            scaled = _minmax_scaler(df_metrics[col])
            if col == "std":
                # std 越小越好 -> 取反
                scaled = 1.0 - scaled
            norm_df[col] = scaled
        norm_store[hname] = (df_metrics, norm_df)

    result = pd.DataFrame(index=stocks)

    # 保存原始指标（以便审计）
    for hname, (raw_df, _) in norm_store.items():
        for c in raw_df.columns:
            result[f"{hname}_raw_{c}"] = raw_df[c]

    score_cols = []
    for profile, w in weights.items():
        for hname in horizons.keys():
            _, norm_df = norm_store[hname]
            score = (
                w["mean"] * norm_df["mean"].fillna(0.5)
                + w["stability"] * norm_df["std"].fillna(0.5)
                + w["slope"] * norm_df["slope"].fillna(0.5)
                + w["consistency"] * norm_df["positive_ratio"].fillna(0.5)
                + w["last"] * norm_df["last"].fillna(0.5)
            )
            col_name = f"{profile}_{hname}_score"
            result[col_name] = score
            score_cols.append(col_name)

    # 映射到 0-5 的整数星级后转换为仅实心星字符串
    for col in score_cols:
        scores = result[col]
        if star_method == "quantile":
            # 按分位分组（相对排名）
            labels = pd.qcut(scores.rank(method="first"), q=quantile_bins, labels=False, duplicates="drop")
            max_label = labels.max() if labels.notna().any() else 0
            if pd.isna(max_label) or max_label == 0:
                stars_num = pd.Series(0, index=result.index)
            else:
                stars_num = (labels.astype(float) / max_label) * 5.0
        else:
            # 绝对缩放
            scaled = _minmax_scaler(scores.fillna(scores.mean() if scores.notna().any() else 0.5))
            stars_num = scaled * 5.0

        stars_num = stars_num.round().astype(int).clip(0, 5)
        # 直接用本地定义的 _stars_str 映射为字符串，避免 NameError
        result[col.replace("_score", "_stars")] = stars_num.map(_stars_str)

    # 将星星列放在最前，便于查看
    star_cols = [c for c in result.columns if c.endswith("_stars")]
    ordered_cols = star_cols + [c for c in result.columns if c not in star_cols]
    result = result[ordered_cols]

    return result


"""
要点摘要（实现思路）
对每个时长（short/mid/long）计算：均值（mean）、波动（std）、趋势（slope via线性回归）、一致性（positive_ratio）、最新值（last）。
将每个度量在股票间做 min-max 标准化（0-1），然后根据三类客户的偏好用不同权重合成一个 score。
进取型（Aggressive）：更重视均值、趋势、最新值，对波动容忍更高（波动权重低）。
稳健型（Balanced）：均值、趋势、波动、中性权重。
保守型（Conservative）：强调低波动（稳定）和高一致性，趋势和均值权重较低。
将合成 score 映射到 0–5 星（连续 scale，然后 round 到整数星数；也提供可切换为分位数切分的选项）。
返回的 DataFrame 包含：每只股票每个（profile, horizon）的星级，以及各中间指标和原始 score（便于解释）。

说明与可调项建议
窗口长度（short/mid/long）可以按你的数据频率与投资逻辑调整（例如：若 df 是周度数据，则可把 20、60、252 换成 4、13、52 等）。
slope_window：你可以单独设置用于趋势判断的窗口（例如不想用 long_window 的长度）。
权重字典 weights 很容易调节：想让进取型更加追求“高峰值”，就提升 last 权重；想让保守型更稳健就提高 stability。
star_method="quantile"：改为分位数切分能保证每个等级都有样本（按分位百分位划分），适合用在需要相对排名的场景；默认 scale 更绝对，优秀股票会真正接近 5 星，而不是被固定分配。
解释星级含义（默认配置）
5 星：在该风险偏好与时长下，该股票表现非常突出（均值高、上升趋势明显、稳定或与偏好匹配）。
3 星：中性、适合部分配置或观望。
0–1 星：不推荐／不在该偏好与时长下持仓。
"""
#==============================================================================
if __name__=='__main__':
    
    result_gemini=rar_recommend_gemini(df,
        short_term_days = 21,
        mid_term_days = 63,
        long_term_days = 252
        )

# --- 默认的投资者画像逻辑 ---
# 键 = 投资者类型
# 值 = 一个字典，定义了 '长期', '中期', '短期' 分别参考哪些指标
#      (如果提供了多个指标，函数将取其星级平均值)
DEFAULT_INVESTOR_PROFILES = {
    '保守型': {
        '长期': ['long_mean'],
        '中期': ['stability'],
        '短期': ['long_mean', 'stability'] # 逻辑: 长期均值 和 稳定性的平均值
    },
    '稳健型': {
        '长期': ['long_trend'],
        '中期': ['mid_trend'],
        '短期': ['last_val']
    },
    '进取型': {
        '长期': ['mid_trend'],
        '中期': ['short_trend'],
        '短期': ['short_trend', 'last_val'] # 逻辑: 短期趋势 和 最新动量的平均值
    }
}

# (辅助函数 _calc_trend_slope 和 _rank_to_stars 保持不变)
def _calc_trend_slope(series: pd.Series) -> float:
    try:
        series_cleaned = series.dropna()
        if len(series_cleaned) < 2:
            return 0.0
        y = series_cleaned.values
        x = np.arange(len(y))
        slope = np.polyfit(x, y, 1)[0]
        return slope
    except Exception:
        return 0.0

def _rank_to_stars(series: pd.Series) -> pd.Series:
    return pd.qcut(series, 5, labels=False, duplicates='drop').fillna(0).astype(int) + 1

# --- *** 核心修改点 *** ---
# 1. 在函数签名中添加 'investor_profiles' 参数
def rar_recommend_gemini(df: pd.DataFrame, 
                              short_term_days: int = 21,
                              mid_term_days: int = 63,
                              long_term_days: int = 252,
                              investor_profiles: dict = None) -> pd.DataFrame:
    """
    基于时间序列比率（如夏普比率）计算一个多维度的投资推荐。

    参数:
    - df (pd.DataFrame): 索引为日期（升序），列为股票代码，值为比率。
    - short_term_days (int): 定义“短期”的交易日天数。
    - mid_term_days (int): 定义“中期”的交易日天数。
    - long_term_days (int): 定义“长期”的交易日天数。
    - investor_profiles (dict, optional): 
        一个定义了投资者画像逻辑的字典。
        如果不提供，将使用 DEFAULT_INVESTOR_PROFILES。
        结构: {'类型': {'长期': [指标1], '中期': [指标2], '短期': [指标3, 指标4]}}
        有效指标: 'long_mean', 'long_trend', 'mid_trend', 'short_trend', 'last_val', 'stability'

    返回:
    - pd.DataFrame: 一个单层索引的DataFrame，显示每只股票的星级评价。
    """
    
    # --- 0. & 1. 安全检查和窗口定义 (不变) ---
    total_rows = len(df)
    if not (short_term_days < mid_term_days < long_term_days):
        raise ValueError("时间窗口必须按顺序递增: short < mid < long。")
    if total_rows < long_term_days:
        raise ValueError(f"DataFrame的数据长度 ({total_rows}) 小于所要求的 'long_term_days' ({long_term_days})。")

    df_long = df.iloc[-long_term_days:]
    df_mid = df.iloc[-mid_term_days:]
    df_short = df.iloc[-short_term_days:]
    
    # --- 2. 计算核心统计指标 (不变) ---
    metrics = pd.DataFrame(index=df.columns)
    metrics['long_mean'] = df_long.mean()
    metrics['long_trend'] = df_long.apply(_calc_trend_slope, axis=0)
    metrics['mid_trend'] = df_mid.apply(_calc_trend_slope, axis=0)
    metrics['short_trend'] = df_short.apply(_calc_trend_slope, axis=0)
    metrics['last_val'] = df.iloc[-1]
    metrics['stability'] = 1 / (df.std() + 1e-6) 

    # --- 3. 将所有指标转换为 1-5 星评级 (不变) ---
    stars = pd.DataFrame(index=df.columns)
    for col in metrics.columns:
        stars[col] = _rank_to_stars(metrics[col])

        
    # --- 4. 构建推荐逻辑与输出 (***核心修改点***) ---
    
    # 如果用户没有传入自定义画像，就使用我们定义的默认值
    if investor_profiles is None:
        investor_profiles = DEFAULT_INVESTOR_PROFILES
        
    # 动态创建输出DataFrame的列
    single_level_columns = []
    # 我们固定周期的顺序，以保证输出的列序一致
    timeframes = ['短期', '中期', '长期'] 
    
    for investor_type in investor_profiles.keys():
        for timeframe in timeframes:
            single_level_columns.append(f"{investor_type}-{timeframe}")

    reco_df_int = pd.DataFrame(index=df.columns, columns=single_level_columns, dtype=int)

    # 动态应用画像逻辑
    for investor_type, logic_map in investor_profiles.items():
        for timeframe, metric_list in logic_map.items():
            
            # 检查指标是否有效
            valid_metrics = [m for m in metric_list if m in stars.columns]
            if not valid_metrics:
                # 如果一个有效的指标都没有，就给0星
                final_star_value = 0 
            
            # 计算星级
            elif len(valid_metrics) == 1:
                # 1. 逻辑：直接映射
                final_star_value = stars[valid_metrics[0]]
            else:
                # 2. 逻辑：平均值
                summed_stars = stars[valid_metrics].sum(axis=1)
                final_star_value = (summed_stars / len(valid_metrics)).round().astype(int)
            
            # 分配到输出列
            col_name = f"{investor_type}-{timeframe}"
            reco_df_int[col_name] = final_star_value

    # --- 5. 格式化输出 (不变) ---
    def format_stars(val):
        safe_val = max(0, min(5, int(val)))
        return "★" * safe_val

    return reco_df_int.applymap(format_stars)

"""
核心逻辑：
计算关键指标：计算每个资产的长期、中期、短期的平均表现（均值）、表现趋势（斜率）、近期动量（最新值）和稳定性（标准差的倒数）。
五星评级：将所有股票在同一指标上进行横向对比，使用分位数（pd.qcut）将它们分为5档，并转换为1-5星。
匹配推荐逻辑：
保守型 (Conservative)：看重长期的、稳定的高表现。
稳健型 (Moderate)：看重中长期的、确定的上升趋势。
进取型 (Aggressive)：看重短中期的、强劲的上升势头和动量。

"""
#==============================================================================
if __name__=='__main__':
    ticker=['300308.SZ', '300502.SZ', '000063.SZ', '600941.SS', '600050.SS']
    start='L2Y'; end='today'
    indicator='sharpe'
    
    ret_type="Annual Adj Ret%"; RF=0; regression_period=365
    mktidx='auto'
    source='auto'; ticker_type='auto'
    
    short_term=21; middle_term=63; long_term=252
    AI_model=None
    
    facecolor='papayawhip'
    
    start='2024-10-31'; end='2025-10-31'
    
    result=security_recommend_rar(ticker,start,end,indicator='sharpe')
    
def security_recommend(ticker: list,
                           start: str = 'L3Y',end: str ='today',
                           
                           indicator: str = 'sharpe',#默认夏普比率
                           ret_type="Annual Adj Ret%",RF=0,
                           #仅用于alpha和treynor
                           regression_period=365,mktidx='auto',
                           source='auto',ticker_type='auto',
                           
                           short_term: int =21*3,#默认1个季度
                           middle_term: int =21*3*4,#默认1年
                           long_term: int =21*3*4*3,#默认3年
                           
                           AI_model: None | list = None,#默认使用全部AI模型
                           
                           facecolor='papayawhip',
                           ):
    """
    套壳函数security_recommend_rar，可扩展模式
    
    功能：基于指定的风险调整指标indicator，对ticker中指定的诸多证券进行评价。
        评价结果以星星个数标示，最多五颗星，星星个数越多，评价就越高！
    评价算法：基于对各个证券在观察期（从start到end日期）中的具体表现，借用多种AI大模型
        算法进行综合分析，每种算法给出独立评价。
        目前支持的AI大模型算法：ChatGPT，Gemini，Copilot。
    评价明细：分别给出各个AI大模型算法基于投资者风险偏好和希冀的投资期间的评价明细。
    评价汇总：对评价明细进行打分汇总，便于直观解读，仅供参考。
    投资者风险偏好：分为三大类（进取型，稳健型和保守型）。
        进取型的定义：追求尽可能高的收益，为此可以承受更高的风险；
        稳健型的定义：追求尽可能高的收益-风险性价比，可以承受相应的风险；
        保守型的定义：在尽可能低风险的前提下最求尽可能高的收益。
        注意：这三种投资者风险偏好均受到风险调整指标indicator的总体制约！
            在不同风险调整指标indicator的语境下，这三种投资者风险偏好的结果可能有所不同！
    希冀的投资期间：分为短期（默认1个季度）、中期（默认1年）和长期（默认3年）三种期间。
        可自行定义天数（注意天数为交易日）。
    
    入口参数：
        ticker：待选的证券列表，可为行业指数、股票代码、上市的债券和基金代码列表。
            对于未上市的行业指数，仅支持中国的申万宏源行业分类。
            如果发生债券和基金代码与其他类别证券代码重复的情形，可用ticker_type强制指定优先类别。
        ticker_type：指定ticker的证券类别优先顺序，默认系统自动识别（auto）。
            如果系统识别错误，可手动强行指定基金（fund）或债券（bond），可以统一指定，也可逐个指定。
        source：样本数据来源，默认系统自动决定（auto）。
            如果需要，可以手动强行指定来源为新浪（sina）、斯杜克（stooq）或雅虎（yahoo）等。
        start和end：观察期的开始和结束日期。
            注意观察期内的交易日数目不得少于长期投资需要的交易日天数。
        indicator：支持四种最常见的风险调整指标。sharpe（夏普比率），sortino（索替诺比率）
            alpha（阿尔法指标），treynor（特雷诺比率）。
        以下参数仅用于阿尔法指标和特雷诺比率中计算贝塔系数：
            ret_type：收益率种类，默认年化收益率（Annual Adj Ret%）
            RF：无风险利率，默认不使用（0）。粗略推荐可不使用，对推荐结果影响不大。
            regression_period：CAPM回归期间，默认一年（365个日历日）
            mktidx：CAPM回归使用的大盘指数，默认系统自动决定（auto）,也可自行指定。
        以下参数用于指定希冀的投资期间：分为短期、中期和长期三种情形。
            short_term为短期，默认1个季度（63个交易日，平均每月按21个交易日计算）；
            middle_term为中期,默认1年（252个交易日）；
            long_term为长期，默认3年（252*3个交易日）。
        AI_model：使用的AI大模型算法，默认使用全部可用的算法。
            支持chatgpt、gemini和copilit，可以手动指定其中一部分。
        facecolor：指定输出表格的背景颜色，默认木瓜色（papayawhip，一种柔和的浅橙黄色）。
            常用的还有烟白色（whitesmoke）
            支持matplotlib内置的约140种颜色，支持十六进制颜色码，但并非所有颜色都好看。
            
    输出参数：
        result_dict：各个AI大模型算法的评价明细
        result_overall：各个AI大模型算法的评价汇总结果
    """
    # 检查入口参数

    rar_list=['sharpe','sortino','alpha','treynor']
    if indicator.lower() in rar_list:
        result_dict, result_overall=security_recommend_rar(
            ticker=ticker,
            start=start,end=end,
            indicator=indicator,
            
            ret_type=ret_type,RF=RF,
            regression_period=regression_period,mktidx=mktidx,
            
            source=source,ticker_type=ticker_type,
                                   
            short_term=short_term,
            middle_term=middle_term,
            long_term=long_term,
            
            AI_model=AI_model,
                                   
            facecolor=facecolor,
           )
    else:
        print(f"  #Error(): unsupported rar indicator {indicator}")
        return None,None
        
    return result_dict, result_overall
    
def security_recommend_rar(ticker: list,
                           start: str = 'L2Y',end: str ='today',
                           
                           indicator: str = 'sharpe',#默认夏普比率
                           ret_type="Annual Adj Ret%",RF=0,
                           #仅用于alpha和treynor
                           regression_period=365,mktidx='auto',
                           source='auto',ticker_type='auto',
                           
                           short_term: int =21,#默认1个月
                           middle_term: int =63,#默认1个季度
                           long_term: int =252,#默认1年
                           
                           AI_model: None | list = None,#默认使用全部AI模型
                           
                           facecolor='papayawhip',
                           ):
    """
    功能：基于RAR指标、投资期限长短和投资者风险偏好对证券打分，并给出星星个数
    参数：
    indicator: 默认'sharpe',夏普比率。还支持'sortino'、'alpha'、'treynor'。
    start/end: 样本数据的抓取期间，默认近2年
    short_term/middle_term/long-term：投资期限短期、中期、长期的日历日天数
        默认1个月、1个季度和1年
    AI_model: 默认使用全部模型（chatgpt,gemini和copilot），可单独指定
    
    输出：星星列表
    """
    # 处理入口参数
    start,end=start_end_preprocess(start,end)
    
    # 调整抓取数据的开始日期，确保有足够的数据应对long_term
    from datetime import datetime
    # 将字符串转换为日期对象
    d1 = datetime.strptime(start, "%Y-%m-%d").date()
    d2 = datetime.strptime(end, "%Y-%m-%d").date()
    days_diff = (d2 - d1).days
    
    days_diff2=days_diff - int(long_term / 240 *365 + 0.5)
    
    if days_diff2 < 0:
        if indicator in ['alpha','treynor']:
            # 这两个指标要求进行CAPM回归，需要更多样本数据
            start1=date_adjust(start,adjust=days_diff2*2)
        else:
            start1=date_adjust(start,adjust=days_diff2)
    else:
        start1=start
    
    # 处理AI_model
    if AI_model is None:
        AI_model=['chatgpt','gemini','copilot']
    elif isinstance(AI_model,str):
        AI_model=[AI_model]
    
    # 抓取数据并计算RAR
    try:
        df,_=compare_mticker_1rar(ticker=ticker,start=start1,end=end,
                                  
                                  rar=indicator, \
                                  ret_type=ret_type,RF=RF,
                                  regression_period=regression_period, \
                                      
                                  mktidx=mktidx,source=source,
                                  ticker_type=ticker_type,
                                  graph=False,printout=False, \
                                  )
    except:
        print(f"   #Error(security_recommend_rar): problem incurred for {ticker}")
        return None
        
    if df is None:
        print(f"   Sorry, info not found for {ticker}")
        return None
    elif len(df) == 0:
        print(f"   Sorry, zero info found for {ticker}")
        return None
        
    df1=df.tail(long_term)
    
    df1_start=df1.index[0]; df1_start=df1_start.strftime("%Y-%m-%d")
    # 记录实际抓取的数据的最差情形
    # 找出每列最后一个非空值的索引
    last_nonnull_idx = df1.apply(lambda col: col.last_valid_index())
    # 取最小的日期
    min_last_date = last_nonnull_idx.min()    
    df1_end=min_last_date; df1_end=df1_end.strftime("%Y-%m-%d")

    lang=check_language()
    print(f"  Recommending using AI model algorithms ...")
    result_dict={}
    for ai in AI_model:
        if ai.lower() == 'chatgpt':
            
            df_tmp=rar_recommend_chatgpt(
                df1,
                short_window=short_term,
                mid_window=middle_term,
                long_window=long_term,
                slope_window = None,
                star_method = "scale",  # "scale" or "quantile"
                quantile_bins = 5
                )
            df_tmp["证券"]=df_tmp.index
            
            star_cols = [col for col in df_tmp.columns if col.endswith("_stars")]
            df_tmp2=df_tmp[["证券"]+star_cols]
            
            result=df_tmp2.rename(columns={
                '证券':text_lang('证券','Security'),
                'Aggressive_short_stars':text_lang('进取(短)','Agg(ST)'),
                'Aggressive_mid_stars':text_lang('进取(中)','Agg(MT)'),
                'Aggressive_long_stars':text_lang('进取(长)','Agg(LT)'),
                
                'Balanced_short_stars':text_lang('稳健(短)','Prud(ST)'),
                'Balanced_mid_stars':text_lang('稳健(中)','Prud(MT)'),
                'Balanced_long_stars':text_lang('稳健(长)','Prud(LT)'),
                
                'Conservative_short_stars':text_lang('保守(短)','Cons(ST)'),
                'Conservative_mid_stars':text_lang('保守(中)','Cons(MT)'),
                'Conservative_long_stars':text_lang('保守(长)','Cons(LT)'),
                })

        if ai.lower() == 'gemini':
            #print(f"\n  Evaluating recommendation using {ai} model algorithm ...")
            df_tmp=rar_recommend_gemini(
                df1,
                short_term_days=short_term,
                mid_term_days=middle_term,
                long_term_days=long_term,
                investor_profiles = None)

            df_tmp_cols=list(df_tmp)
            df_tmp["证券"]=df_tmp.index
            
            aggressive_cols=["证券",'进取型-短期','进取型-中期','进取型-长期']
            conservative_cols=['保守型-短期','保守型-中期','保守型-长期']
            # 移动字段排列顺序：进取型放最前面，保守型放最后面
            new_order1 = aggressive_cols + [col for col in df_tmp_cols if col not in aggressive_cols]   
            new_order2 = [col for col in new_order1 if col not in conservative_cols] + conservative_cols
            df_tmp2=df_tmp[new_order2]
            
            result=df_tmp2.rename(columns={
                '证券':text_lang('证券','Security'),
                '进取型-短期':text_lang('进取(短)','Agg(ST)'),
                '进取型-中期':text_lang('进取(中)','Agg(MT)'),
                '进取型-长期':text_lang('进取(长)','Agg(LT)'),
                
                '稳健型-短期':text_lang('稳健(短)','Prud(ST)'),
                '稳健型-中期':text_lang('稳健(中)','Prud(MT)'),
                '稳健型-长期':text_lang('稳健(长)','Prud(LT)'),
                
                '保守型-短期':text_lang('保守(短)','Cons(ST)'),
                '保守型-中期':text_lang('保守(中)','Cons(MT)'),
                '保守型-长期':text_lang('保守(长)','Cons(LT)'),
                })
            
        if ai.lower() == 'copilot':
            #print(f"\n  Evaluating recommendation using {ai} model algorithm ...")
            window_lengths={"short": short_term, "mid": middle_term, "long": long_term}
            df_tmp=rar_recommend_copilot(
                    df1,
                    window_lengths=window_lengths,
                    profiles = None,
                    return_scores = False,
                    min_obs = 10,
                   )
            
            df_tmp_cols=list(df_tmp)
            df_tmp["证券"]=df_tmp.index
            aggressive_cols=["证券",'aggressive_short','aggressive_mid','aggressive_long']
            conservative_cols=['conservative_short','conservative_mid','conservative_long']
            # 移动字段排列顺序：进取型放最前面，保守型放最后面
            new_order1 = aggressive_cols + [col for col in df_tmp_cols if col not in aggressive_cols]   
            new_order2 = [col for col in new_order1 if col not in conservative_cols] + conservative_cols
            df_tmp2=df_tmp[new_order2]
            
            result=df_tmp2.rename(columns={
                '证券':text_lang('证券','Security'),
                'aggressive_short':text_lang('进取(短)','Agg(ST)'),
                'aggressive_mid':text_lang('进取(中)','Agg(MT)'),
                'aggressive_long':text_lang('进取(长)','Agg(LT)'),
                
                'balanced_short':text_lang('稳健(短)','Prud(ST)'),
                'balanced_mid':text_lang('稳健(中)','Prud(MT)'),
                'balanced_long':text_lang('稳健(长)','Prud(LT)'),
                
                'conservative_short':text_lang('保守(短)','Cons(ST)'),
                'conservative_mid':text_lang('保守(中)','Cons(MT)'),
                'conservative_long':text_lang('保守(长)','Cons(LT)'),
                })
            
        # 去掉"申万"/"指数"字样
        sec_fld=text_lang('证券','Security')
        remove_list = ["申万", "指数"]
        for word in remove_list:
            result[sec_fld] = result[sec_fld].str.replace(word, "", regex=False)
        # 翻译行业指数名称
        """
        if lang == 'English':
            name_dict=sw_name_dict()
            result[sec_fld]=result[sec_fld].map(lambda v: name_dict.get(v, v)) #找不到时返回原值
        """
        # 记录各个AI模型的结果            
        result_dict[ai]=result
            
        titletxt0=text_lang("热点证券推荐","Security Recommend")
        rar_text={'sharpe':text_lang('夏普比率','Sharpe Ratio'),
                  'sortino':text_lang('索替诺比率','Sortino Ratio'),
                  'treynor':text_lang('特雷诺比率','Treynor Ratio'),
                  'alpha':text_lang('阿尔法指标','Jensen Alpha'),
                  }
        rar_name=rar_text[indicator.lower()]
        AI_text={'chatgpt':'ChatGPT',
                 'gemini':'Gemini',
                 'copilot':'Copilot',
                 }
        AI_name=AI_text[ai.lower()]
        
        based_on_txt=text_lang("基于","By ")
        and_txt=text_lang("和"," and ")
        model_txt=text_lang("大模型算法"," Algorithm")
        titletxt=f"{titletxt0}: {based_on_txt}{rar_name}{and_txt}{AI_name}{model_txt}"

        ft0=f"{text_lang("注：","[Note] ")}"
        """
        short_term_txt=f"{text_lang("短期","ST=")}{short_term}{text_lang("个交易日"," t-days")}"
        mid_term_txt=f"{text_lang("中期","MT=")}{middle_term}{text_lang("个交易日"," t-days")}"
        long_term_txt=f"{text_lang("长期","LT=")}{long_term}{text_lang("个交易日"," t-days")}"
        """
        short_term_txt=f"{text_lang("短期","ST=")}{short_term}"
        mid_term_txt=f"{text_lang("中期","MT=")}{middle_term}"
        long_term_txt=f"{text_lang("长期","LT=")}{long_term}{text_lang("个交易日"," t-days")}"
        
        ft1=short_term_txt+', '+mid_term_txt+', '+long_term_txt
        
        ft2_cn=f"观察期{df1_start}至{df1_end}"
        ft2_en=f"Sampling: {df1_start} to {df1_end}"
        ft2=text_lang(ft2_cn,ft2_en)
        
        import datetime; todaydt = datetime.date.today()
        ft9=text_lang("数据来源: 申万宏源","Data source: SWHYSC")
        
        footnote=ft0+ft1+'; '+ft2+'; '+ft9+', '+str(todaydt)
        
        df_display_CSS(result,titletxt=titletxt,footnote=footnote,
                       facecolor=facecolor,
                       first_col_align='left',second_col_align='right',
                       last_col_align='right',other_col_align='right',
                       titile_font_size='16px',heading_font_size='13px',
                       data_font_size='13px',footnote_font_size='12px')
    
    # 对各个AI大模型的星星个数汇总，生成综合汇总表，但排除列sec_fld
    result_overall=combine_star_counts(result_dict,keep_cols=[sec_fld])
    
    ai_num=len(result_dict)
    max_points_cn=f"最高{5*ai_num}分"
    max_points_en=f"Max {5*ai_num} Points"
    max_points=text_lang(max_points_cn,max_points_en)
    
    star5txt_cn=f"(*个数为五星评价次数)"
    star5txt_en=f"(* = Counts of 5-Star)"
    star5txt=text_lang(star5txt_cn,star5txt_en)
    
    titletxt_overall=f"{titletxt0}: {based_on_txt}{rar_name}, {max_points}{star5txt}"
    
    df_display_CSS(result_overall,titletxt=titletxt_overall,footnote=footnote,
                   facecolor=facecolor,
                   first_col_align='left',second_col_align='right',
                   last_col_align='right',other_col_align='right',
                   titile_font_size='16px',heading_font_size='13px',
                   data_font_size='13px',footnote_font_size='12px')
    

    return result_dict, result_overall


#==============================================================================

def combine_star_counts0(result_dict: dict, keep_cols: list[str] = None) -> pd.DataFrame:
    """
    将多个包含 '★' 字符的 DataFrame 按位置汇总为计数结果，计数结果不加星号
    同时保留指定列（这些列在所有 df 中内容相同）。

    参数：
        result_dict : dict[str, pd.DataFrame]
            各个 DataFrame（索引和列一致）
        keep_cols : list[str], 可选
            不参与星号统计的列，这些列将按原样保留（保留一份）

    返回：
        pd.DataFrame : 汇总后的 DataFrame
    """
    if not result_dict:
        return pd.DataFrame()

    # 取第一个 df 作为结构参考
    first_df = next(iter(result_dict.values()))
    keep_cols = keep_cols or []

    # 分离待统计列
    star_cols = [col for col in first_df.columns if col not in keep_cols]

    star_counts = []
    for df in result_dict.values():
        # 仅对 star_cols 统计
        df_star = df[star_cols].applymap(lambda x: len(x) if isinstance(x, str) else 0)
        df_star = df_star.astype(int)
        star_counts.append(df_star)

    # 汇总相加（安全方式）
    result_overall = star_counts[0].copy()
    for df_star in star_counts[1:]:
        result_overall = result_overall.add(df_star, fill_value=0)

    result_overall = result_overall.fillna(0).astype(int)

    # 把 keep_cols 加回去（保持原有顺序）
    if keep_cols:
        # 只保留一份（假设内容相同）
        keep_part = first_df[keep_cols].copy()
        # 保证列顺序：先 keep_cols 后 star_cols
        result_overall = pd.concat([keep_part, result_overall], axis=1)

    return result_overall
#==============================================================================

def combine_star_counts1(result_dict: dict, keep_cols: list[str] = None, star_char: str = '★') -> pd.DataFrame:
    """
    汇总多个包含星级字符的 DataFrame：
    - 统计每个单元格中星星数量之和；
    - 若任一 df 中出现 '★★★★★'，则在结果数字 后 加 '*'；
    - 可指定不参与统计的列（keep_cols）原样保留。

    参数：
        result_dict : dict[str, pd.DataFrame]
            各个 DataFrame（索引和列一致）
        keep_cols : list[str], optional
            不参与星号统计的列，将原样保留。
        star_char : str, default '★'
            计数的星号字符。
    返回：
        pd.DataFrame
    """
    if not result_dict:
        return pd.DataFrame()

    first_df = next(iter(result_dict.values()))
    keep_cols = keep_cols or []
    star_cols = [col for col in first_df.columns if col not in keep_cols]

    # 初始化汇总 DataFrame
    sum_df = None
    mark_df = None  # 用于记录每个单元格出现了几次“★★★★★”

    for df in result_dict.values():
        df_star = df[star_cols].applymap(lambda x: len(x) if isinstance(x, str) else 0)
        df_star = df_star.astype(int)

        # 标记该 df 中哪些位置是 5 颗星
        df_mark = df[star_cols].applymap(lambda x: 1 if isinstance(x, str) and x == star_char * 5 else 0)

        if sum_df is None:
            sum_df = df_star.copy()
            mark_df = df_mark.copy()
        else:
            sum_df = sum_df.add(df_star, fill_value=0)
            mark_df = mark_df.add(df_mark, fill_value=0)

    # 构造输出 DataFrame
    sum_df = sum_df.fillna(0).astype(int)
    mark_df = mark_df.fillna(0).astype(int)

    # 将数量和标记合并为字符串
    result_overall = sum_df.astype(str)
    for col in star_cols:
        result_overall[col] = result_overall[col] + mark_df[col].apply(lambda n: '*' * n if n > 0 else '')

    # 添加保留列（保持原顺序）
    if keep_cols:
        keep_part = first_df[keep_cols].copy()
        result_overall = pd.concat([keep_part, result_overall], axis=1)

    return result_overall
#==============================================================================

def combine_star_counts(result_dict: dict, keep_cols: list[str] = None, star_char: str = '★') -> pd.DataFrame:
    """
    汇总多个包含星级字符的 DataFrame：
    - 统计每个单元格中星星数量之和；
    - 若任一 df 中出现 '★★★★★'，则在结果数字 前 加 '*'；
    - 若多份 df 同一位置出现 '★★★★★'，累积多个 '*'；
    - 可指定不参与统计的列（keep_cols）原样保留。

    参数：
        result_dict : dict[str, pd.DataFrame]
            各个 DataFrame（索引和列一致）
        keep_cols : list[str], optional
            不参与星号统计的列，将原样保留。
        star_char : str, default '★'
            计数的星号字符。
    返回：
        pd.DataFrame
    """
    if not result_dict:
        return pd.DataFrame()

    first_df = next(iter(result_dict.values()))
    keep_cols = keep_cols or []
    star_cols = [col for col in first_df.columns if col not in keep_cols]

    sum_df = None   # 星号数量
    mark_df = None  # '★★★★★' 次数

    for df in result_dict.values():
        # 每格星数
        df_star = df[star_cols].applymap(lambda x: len(x) if isinstance(x, str) else 0)
        df_star = df_star.astype(int)

        # 每格五星标记
        df_mark = df[star_cols].applymap(lambda x: 1 if isinstance(x, str) and x == star_char * 5 else 0)

        if sum_df is None:
            sum_df = df_star.copy()
            mark_df = df_mark.copy()
        else:
            sum_df = sum_df.add(df_star, fill_value=0)
            mark_df = mark_df.add(df_mark, fill_value=0)

    sum_df = sum_df.fillna(0).astype(int)
    mark_df = mark_df.fillna(0).astype(int)

    # 把标记加到前面
    result_overall = sum_df.astype(str)
    for col in star_cols:
        result_overall[col] = mark_df[col].apply(lambda n: '*' * n if n > 0 else '') + result_overall[col]

    # 添加保留列（保持原顺序）
    if keep_cols:
        keep_part = first_df[keep_cols].copy()
        result_overall = pd.concat([keep_part, result_overall], axis=1)

    return result_overall

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
