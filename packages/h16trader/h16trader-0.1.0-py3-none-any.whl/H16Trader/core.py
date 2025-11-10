import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
from enum import Enum
import warnings

class Indicators:
    """
    技术指标计算类
    提供各种常用技术分析指标的计算方法，所有方法均为静态方法

    技术指标分类：
    - 趋势指标：SMA, EMA, MACD, ADX 等
    - 动量指标：RSI, Stochastic, Williams %R, CCI 等
    - 波动率指标：Bollinger Bands, ATR 等
    - 成交量指标：OBV 等
    - 支撑阻力指标：Fibonacci, Pivot Points 等
    """

    class MAType(Enum):
        """移动平均线类型枚举"""
        SMA = "sma"  # 简单移动平均
        EMA = "ema"  # 指数移动平均
        WMA = "wma"  # 加权移动平均
        DEMA = "dema"  # 双指数移动平均
        TEMA = "tema"  # 三指数移动平均

    @staticmethod
    def sma(prices: Union[List[float], pd.Series, np.ndarray],
            period: int) -> np.ndarray:
        """
        简单移动平均线 (Simple Moving Average - SMA)

        含义：
        SMA是最基本的技术指标，通过计算指定周期内价格的平均值来平滑价格数据，
        帮助识别趋势方向和强度。SMA对历史所有数据给予相同权重。

        计算公式：
        SMA_t = (P_t + P_{t-1} + ... + P_{t-n+1}) / n
        其中：P为价格，n为周期

        应用场景：
        1. 趋势识别：价格在SMA上方为上升趋势，下方为下降趋势
        2. 支撑阻力：SMA可作为动态支撑阻力位
        3. 交叉信号：短期SMA上穿长期SMA为买入信号，反之为卖出信号

        Args:
            prices: 价格序列，通常是收盘价，支持列表、pandas.Series或numpy数组
            period: 计算周期，决定SMA的平滑程度

        Returns:
            SMA序列，长度与输入相同，前period-1个位置为np.nan（因为数据不足）

        代码详解（以SMA为例）：
        """
        # 1. 输入验证：检查数据长度是否足够计算SMA
        #    如果数据点少于周期，返回全为NaN的数组
        if len(prices) < period:
            return np.array([np.nan] * len(prices))

        # 2. 数据转换：将各种输入类型统一转换为numpy数组
        #    确保后续计算的一致性
        prices_array = np.array(prices)

        # 3. 初始化结果数组：创建与输入长度相同的数组，初始值设为NaN
        #    NaN表示该位置无法计算有效的SMA值
        sma_values = np.full(len(prices), np.nan)

        # 4. 核心计算循环：从第period-1个位置开始计算（0-based索引）
        #    对于每个位置i，计算从i-period+1到i的period个价格的平均值
        for i in range(period - 1, len(prices)):
            # 4.1 切片获取当前窗口内的价格数据
            #     prices_array[i - period + 1:i + 1] 获取从i-period+1到i的period个价格
            window_prices = prices_array[i - period + 1:i + 1]

            # 4.2 计算窗口内价格的算术平均值
            #     np.mean()函数计算平均值
            sma_values[i] = np.mean(window_prices)

        # 5. 返回结果：包含SMA值的数组，前period-1个为NaN
        return sma_values

    @staticmethod
    def ema(prices: Union[List[float], pd.Series, np.ndarray],
            period: int) -> np.ndarray:
        """
        指数移动平均线 (Exponential Moving Average - EMA)

        含义：
        EMA是一种加权移动平均，对近期价格给予更高权重，比SMA对价格变化更敏感。
        这使得EMA能更快地反应价格趋势的变化。

        计算公式：
        EMA_t = (P_t * k) + (EMA_{t-1} * (1 - k))
        其中：k = 2 / (n + 1) 为平滑系数，n为周期

        Args:
            prices: 价格序列
            period: EMA周期

        Returns:
            EMA序列
        """
        if len(prices) < period:
            return np.array([np.nan] * len(prices))

        prices_array = np.array(prices)
        ema_values = np.full(len(prices), np.nan)

        # 平滑系数：决定新价格和旧EMA的权重
        # 周期越小，k越大，对新价格反应越敏感
        multiplier = 2.0 / (period + 1)

        # 第一个EMA值使用SMA计算（因为没有前一个EMA值）
        ema_values[period - 1] = np.mean(prices_array[:period])

        # 递归计算后续EMA值
        for i in range(period, len(prices)):
            # 新EMA = 当前价格 * 平滑系数 + 前一个EMA * (1 - 平滑系数)
            ema_values[i] = (prices_array[i] * multiplier +
                             ema_values[i - 1] * (1 - multiplier))

        return ema_values

    @staticmethod
    def rsi(prices: Union[List[float], pd.Series, np.ndarray],
            period: int = 14) -> np.ndarray:
        """
        相对强弱指数 (Relative Strength Index - RSI)

        含义：
        RSI是动量震荡指标，测量价格变动的速度和幅度，用于识别超买超卖状态。
        RSI在0-100之间波动，通常30以下为超卖（可能反弹），70以上为超买（可能回调）。

        计算公式：
        RSI = 100 - (100 / (1 + RS))
        RS = 平均涨幅 / 平均跌幅

        Args:
            prices: 价格序列
            period: RSI周期，默认14

        Returns:
            RSI序列，值在0-100之间
        """
        if len(prices) < period + 1:
            return np.array([np.nan] * len(prices))

        prices_array = np.array(prices)

        # 计算价格变化：今天价格 - 昨天价格
        deltas = np.diff(prices_array)

        # 分离上涨和下跌：上涨为正数，下跌为负数（取绝对值）
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        rsi_values = np.full(len(prices), np.nan)

        # 计算初始平均值（前period个变化）
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        # 计算第一个RSI值
        if avg_loss == 0:
            # 如果期间没有下跌，RSI为100
            rsi_values[period] = 100
        else:
            rs = avg_gain / avg_loss  # 相对强度
            rsi_values[period] = 100 - (100 / (1 + rs))

        # 递归计算后续RSI值（使用平滑平均）
        for i in range(period + 1, len(prices)):
            gain = gains[i - 1]  # 注意索引调整，因为deltas比prices短1
            loss = losses[i - 1]

            # 平滑平均：新平均值 = (旧平均值 * (n-1) + 新值) / n
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

            if avg_loss == 0:
                rsi_values[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi_values[i] = 100 - (100 / (1 + rs))

        return rsi_values

    @staticmethod
    def macd(prices: Union[List[float], pd.Series, np.ndarray],
             fast_period: int = 12, slow_period: int = 26,
             signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        移动平均收敛散度 (Moving Average Convergence Divergence - MACD)

        含义：
        MACD是趋势跟踪动量指标，显示两个移动平均线之间的关系。
        由三部分组成：
        - MACD线：快EMA - 慢EMA
        - 信号线：MACD线的EMA
        - 柱状图：MACD线 - 信号线

        交易信号：
        - MACD线上穿信号线：买入信号
        - MACD线下穿信号线：卖出信号
        - 柱状图变化：动量强度

        Args:
            prices: 价格序列
            fast_period: 快线周期，默认12
            slow_period: 慢线周期，默认26
            signal_period: 信号线周期，默认9

        Returns:
            (MACD线, 信号线, 柱状图)
        """
        # 计算快慢EMA
        ema_fast = Indicators.ema(prices, fast_period)
        ema_slow = Indicators.ema(prices, slow_period)

        # MACD线 = 快EMA - 慢EMA
        macd_line = ema_fast - ema_slow

        # 信号线 = MACD线的EMA
        # 先过滤掉NaN值，计算有效部分的EMA
        valid_macd = macd_line[~np.isnan(macd_line)]
        signal_line = Indicators.ema(valid_macd, signal_period)

        # 对齐长度：信号线比MACD线短，需要填充前面的NaN
        full_signal_line = np.full(len(prices), np.nan)
        start_idx = slow_period - 1 + signal_period - 1  # 计算信号线开始的有效位置
        full_signal_line[start_idx:start_idx + len(signal_line)] = signal_line

        # 柱状图 = MACD线 - 信号线
        histogram = macd_line - full_signal_line

        return macd_line, full_signal_line, histogram

    @staticmethod
    def bollinger_bands(prices: Union[List[float], pd.Series, np.ndarray],
                        period: int = 20,
                        num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        布林带 (Bollinger Bands)

        含义：
        布林带由三条线组成，基于价格的移动平均和标准差。
        - 中轨：SMA
        - 上轨：SMA + 标准差倍数
        - 下轨：SMA - 标准差倍数

        应用场景：
        1. 波动率测量：带宽变宽表示波动率增加
        2. 超买超卖：价格触及上轨可能超买，触及下轨可能超卖
        3. 趋势确认：价格在布林带中轨上方为上升趋势

        Args:
            prices: 价格序列
            period: 计算周期，默认20
            num_std: 标准差倍数，默认2.0（约95%置信区间）

        Returns:
            (上轨, 中轨, 下轨)
        """
        if len(prices) < period:
            return (np.array([np.nan] * len(prices)),
                    np.array([np.nan] * len(prices)),
                    np.array([np.nan] * len(prices)))

        prices_array = np.array(prices)

        # 中轨 = SMA
        middle_band = Indicators.sma(prices, period)

        upper_band = np.full(len(prices), np.nan)
        lower_band = np.full(len(prices), np.nan)

        for i in range(period - 1, len(prices)):
            # 计算当前窗口的标准差
            window_prices = prices_array[i - period + 1:i + 1]
            std = np.std(window_prices)

            # 上轨 = 中轨 + 标准差倍数
            upper_band[i] = middle_band[i] + num_std * std
            # 下轨 = 中轨 - 标准差倍数
            lower_band[i] = middle_band[i] - num_std * std

        return upper_band, middle_band, lower_band

    @staticmethod
    def stochastic_oscillator(high: Union[List[float], pd.Series, np.ndarray],
                              low: Union[List[float], pd.Series, np.ndarray],
                              close: Union[List[float], pd.Series, np.ndarray],
                              period: int = 14,
                              smooth_k: int = 3,
                              smooth_d: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """
        随机震荡指标 (Stochastic Oscillator)

        含义：
        随机指标比较当前收盘价在指定周期价格范围中的位置，用于识别超买超卖。
        - %K线：原始随机值
        - %D线：%K线的移动平均

        应用场景：
        - %K < 20：超卖区域，可能反弹
        - %K > 80：超买区域，可能回调
        - %K上穿%D：买入信号
        - %K下穿%D：卖出信号

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 计算周期，默认14
            smooth_k: K线平滑周期，默认3
            smooth_d: D线平滑周期，默认3

        Returns:
            (K线, D线)
        """
        if len(high) < period or len(low) < period or len(close) < period:
            return np.array([np.nan] * len(close)), np.array([np.nan] * len(close))

        high_array = np.array(high)
        low_array = np.array(low)
        close_array = np.array(close)

        k_values = np.full(len(close), np.nan)

        for i in range(period - 1, len(close)):
            # 计算周期内最高价和最低价
            highest_high = np.max(high_array[i - period + 1:i + 1])
            lowest_low = np.min(low_array[i - period + 1:i + 1])

            # %K = (当前收盘价 - 周期最低价) / (周期最高价 - 周期最低价) * 100
            if highest_high != lowest_low:
                k_values[i] = 100 * (close_array[i] - lowest_low) / (highest_high - lowest_low)
            else:
                k_values[i] = 50  # 避免除零错误

        # 平滑K线（%K的移动平均）
        valid_k = k_values[~np.isnan(k_values)]
        k_smoothed = Indicators.sma(valid_k, smooth_k)

        # 计算D线（平滑后K线的移动平均）
        valid_k_smoothed = k_smoothed[~np.isnan(k_smoothed)]
        d_smoothed = Indicators.sma(valid_k_smoothed, smooth_d)

        # 对齐长度（因为平滑操作会缩短序列）
        full_k = np.full(len(close), np.nan)
        full_d = np.full(len(close), np.nan)

        start_idx_k = period - 1 + smooth_k - 1
        start_idx_d = start_idx_k + smooth_d - 1

        full_k[start_idx_k:start_idx_k + len(k_smoothed)] = k_smoothed
        full_d[start_idx_d:start_idx_d + len(d_smoothed)] = d_smoothed

        return full_k, full_d

    @staticmethod
    def atr(high: Union[List[float], pd.Series, np.ndarray],
            low: Union[List[float], pd.Series, np.ndarray],
            close: Union[List[float], pd.Series, np.ndarray],
            period: int = 14) -> np.ndarray:
        """
        平均真实波幅 (Average True Range - ATR)

        含义：
        ATR衡量价格波动性，考虑价格缺口情况，比简单的高低范围更准确。
        用于设置止损位和评估市场波动性。

        计算公式：
        真实波幅(TR) = max(当天高点-当天低点, |当天高点-前一天收盘|, |当天低点-前一天收盘|)
        ATR = TR的移动平均

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: ATR周期，默认14

        Returns:
            ATR序列
        """
        if len(high) < period or len(low) < period or len(close) < period:
            return np.array([np.nan] * len(close))

        high_array = np.array(high)
        low_array = np.array(low)
        close_array = np.array(close)

        # 计算真实波幅(True Range)
        true_ranges = np.zeros(len(high))
        true_ranges[0] = high_array[0] - low_array[0]  # 第一个TR为当日高低差

        for i in range(1, len(high)):
            tr1 = high_array[i] - low_array[i]  # 当日高低差
            tr2 = abs(high_array[i] - close_array[i - 1])  # 当日最高与昨日收盘差
            tr3 = abs(low_array[i] - close_array[i - 1])  # 当日最低与昨日收盘差
            true_ranges[i] = max(tr1, tr2, tr3)  # 取三者最大值

        # 计算ATR（TR的移动平均）
        atr_values = np.full(len(high), np.nan)
        atr_values[period - 1] = np.mean(true_ranges[:period])  # 初始ATR为TR的简单平均

        # 递归计算后续ATR（使用平滑平均）
        for i in range(period, len(high)):
            atr_values[i] = (atr_values[i - 1] * (period - 1) + true_ranges[i]) / period

        return atr_values

    @staticmethod
    def obv(close: Union[List[float], pd.Series, np.ndarray],
            volume: Union[List[float], pd.Series, np.ndarray]) -> np.ndarray:
        """
        能量潮指标 (On-Balance Volume - OBV)

        含义：
        OBV通过成交量变化预测价格变动，基于"成交量先于价格"的假设。
        OBV上升表示买入压力，下降表示卖出压力。

        计算公式：
        如果今日收盘价 > 昨日收盘价：OBV = 前OBV + 今日成交量
        如果今日收盘价 < 昨日收盘价：OBV = 前OBV - 今日成交量
        如果相等：OBV不变

        Args:
            close: 收盘价序列
            volume: 成交量序列

        Returns:
            OBV序列
        """
        if len(close) != len(volume):
            raise ValueError("收盘价和成交量序列长度必须相同")

        close_array = np.array(close)
        volume_array = np.array(volume)

        obv_values = np.zeros(len(close))
        obv_values[0] = volume_array[0]  # 初始OBV为第一日成交量

        for i in range(1, len(close)):
            if close_array[i] > close_array[i - 1]:
                # 价格上涨，成交量加入OBV
                obv_values[i] = obv_values[i - 1] + volume_array[i]
            elif close_array[i] < close_array[i - 1]:
                # 价格下跌，成交量从OBV中减去
                obv_values[i] = obv_values[i - 1] - volume_array[i]
            else:
                # 价格不变，OBV不变
                obv_values[i] = obv_values[i - 1]

        return obv_values

    @staticmethod
    def williams_r(high: Union[List[float], pd.Series, np.ndarray],
                   low: Union[List[float], pd.Series, np.ndarray],
                   close: Union[List[float], pd.Series, np.ndarray],
                   period: int = 14) -> np.ndarray:
        """
        威廉指标 (Williams %R)

        含义：
        威廉指标是动量震荡指标，测量当前收盘价在指定周期价格范围中的位置。
        与随机指标类似，但刻度相反（0到-100）。

        应用场景：
        - %R > -20：超买区域
        - %R < -80：超卖区域

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 计算周期，默认14

        Returns:
            Williams %R序列，值在0到-100之间
        """
        if len(high) < period or len(low) < period or len(close) < period:
            return np.array([np.nan] * len(close))

        high_array = np.array(high)
        low_array = np.array(low)
        close_array = np.array(close)

        williams_r_values = np.full(len(close), np.nan)

        for i in range(period - 1, len(close)):
            highest_high = np.max(high_array[i - period + 1:i + 1])
            lowest_low = np.min(low_array[i - period + 1:i + 1])

            if highest_high != lowest_low:
                # %R = (周期最高价 - 当前收盘价) / (周期最高价 - 周期最低价) * -100
                williams_r_values[i] = -100 * (highest_high - close_array[i]) / (highest_high - lowest_low)
            else:
                williams_r_values[i] = -50  # 避免除零

        return williams_r_values

    @staticmethod
    def cci(high: Union[List[float], pd.Series, np.ndarray],
            low: Union[List[float], pd.Series, np.ndarray],
            close: Union[List[float], pd.Series, np.ndarray],
            period: int = 20) -> np.ndarray:
        """
        商品通道指数 (Commodity Channel Index - CCI)

        含义：
        CCI测量当前价格相对于统计平均价格的偏差，用于识别周期性趋势。

        应用场景：
        - CCI > +100：超买，可能回调
        - CCI < -100：超卖，可能反弹
        - CCI从负值上穿-100：买入信号
        - CCI从正值下穿+100：卖出信号

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 计算周期，默认20

        Returns:
            CCI序列
        """
        if len(high) < period or len(low) < period or len(close) < period:
            return np.array([np.nan] * len(close))

        high_array = np.array(high)
        low_array = np.array(low)
        close_array = np.array(close)

        # 典型价格 = (最高 + 最低 + 收盘) / 3
        typical_price = (high_array + low_array + close_array) / 3

        cci_values = np.full(len(close), np.nan)

        for i in range(period - 1, len(close)):
            # 计算典型价格的移动平均
            sma_tp = np.mean(typical_price[i - period + 1:i + 1])

            # 计算平均偏差
            mean_deviation = np.mean(np.abs(typical_price[i - period + 1:i + 1] - sma_tp))

            if mean_deviation != 0:
                # CCI = (典型价格 - 移动平均) / (0.015 * 平均偏差)
                cci_values[i] = (typical_price[i] - sma_tp) / (0.015 * mean_deviation)
            else:
                cci_values[i] = 0  # 避免除零

        return cci_values

    @staticmethod
    def fibonacci_retracement(high: float, low: float,
                              levels: Optional[List[float]] = None) -> dict:
        """
        斐波那契回撤水平 (Fibonacci Retracement)

        含义：
        基于斐波那契数列的技术分析工具，用于识别潜在的支撑阻力位。
        假设价格在趋势运行后会回调到斐波那契比例位置。

        常用回撤水平：
        0.236, 0.382, 0.5, 0.618, 0.786

        Args:
            high: 趋势高点价格
            low: 趋势低点价格
            levels: 回撤水平列表，默认[0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]

        Returns:
            各回撤水平对应的价格字典
        """
        if levels is None:
            levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]

        price_range = high - low
        retracement_levels = {}

        for level in levels:
            # 回撤价格 = 高点 - 价格区间 * 回撤比例
            price = high - price_range * level
            retracement_levels[f"fib_{level}"] = price

        return retracement_levels

    @staticmethod
    def pivot_points(high: float, low: float, close: float,
                     method: str = "standard") -> dict:
        """
        枢轴点 (Pivot Points)

        含义：
        基于前一天价格计算的支撑阻力位系统，常用于日内交易。

        标准计算方法：
        - 枢轴点 P = (H + L + C) / 3
        - 阻力1 R1 = 2*P - L
        - 支撑1 S1 = 2*P - H
        - 阻力2 R2 = P + (H - L)
        - 支撑2 S2 = P - (H - L)
        - 阻力3 R3 = H + 2*(P - L)
        - 支撑3 S3 = L - 2*(H - P)

        Args:
            high: 前一日最高价
            low: 前一日最低价
            close: 前一日收盘价
            method: 计算方法，"standard"或"fibonacci"

        Returns:
            各枢轴点水平字典
        """
        if method == "standard":
            # 标准枢轴点计算
            pivot = (high + low + close) / 3
            r1 = 2 * pivot - low
            s1 = 2 * pivot - high
            r2 = pivot + (high - low)
            s2 = pivot - (high - low)
            r3 = high + 2 * (pivot - low)
            s3 = low - 2 * (high - pivot)
        elif method == "fibonacci":
            # 斐波那契枢轴点计算
            pivot = (high + low + close) / 3
            r1 = pivot + 0.382 * (high - low)
            s1 = pivot - 0.382 * (high - low)
            r2 = pivot + 0.618 * (high - low)
            s2 = pivot - 0.618 * (high - low)
            r3 = pivot + 1 * (high - low)
            s3 = pivot - 1 * (high - low)
        else:
            raise ValueError("method必须是'standard'或'fibonacci'")

        return {
            "pivot": pivot,
            "r1": r1, "r2": r2, "r3": r3,
            "s1": s1, "s2": s2, "s3": s3
        }

class InstrumentType(Enum):
    """金融工具类型枚举"""
    STOCK = "stock"  # 股票
    FUTURE = "future"  # 期货
    OPTION = "option"  # 期权
    INDEX = "index"  # 指数
    ETF = "etf"  # 交易所交易基金
    FOREX = "forex"  # 外汇
    CRYPTO = "crypto"  # 加密货币
    BOND = "bond"  # 债券
    COMMODITY = "commodity"  # 商品
    WARRANT = "warrant"  # 权证
    SWAP = "swap"  # 互换
    STRUCTURED_PRODUCT = "structured_product"  # 结构化产品
    MUTUAL_FUND = "mutual_fund"  # 共同基金


class EData:
    """
    金融数据实体类
    封装单个金融品种的完整数据序列
    """

    # 标准列名常量
    OPEN = 'open'
    HIGH = 'high'
    LOW = 'low'
    CLOSE = 'close'
    VOLUME = 'volume'
    ADJ_CLOSE = 'adj_close'

    def __init__(self, name: str, instrument_type: Union[InstrumentType, str] = InstrumentType.STOCK):
        """
        初始化金融数据实体

        Args:
            name: 金融品种名称/代码
            instrument_type: 金融工具类型，可以是InstrumentType枚举或字符串
        """
        self.symbol: str = name
        self.instrument_type: InstrumentType = self._parse_instrument_type(instrument_type)
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.table: Optional[pd.DataFrame] = None
        self._data_loaded: bool = False

        # 期货特有属性
        self.multiplier: float = 1.0  # 合约乘数
        self.margin_rate: float = 0.1  # 保证金比例
        self.commission_rate: float = 0.0001  # 手续费率

    def _parse_instrument_type(self, instrument_type: Union[InstrumentType, str]) -> InstrumentType:
        """
        解析金融工具类型

        Args:
            instrument_type: InstrumentType枚举或字符串

        Returns:
            InstrumentType: 解析后的金融工具类型
        """
        if isinstance(instrument_type, InstrumentType):
            return instrument_type
        elif isinstance(instrument_type, str):
            try:
                return InstrumentType(instrument_type.lower())
            except ValueError:
                # 如果字符串不在枚举中，默认为股票类型
                warnings.warn(f"未知的金融工具类型 '{instrument_type}'，使用默认类型 STOCK")
                return InstrumentType.STOCK
        else:
            raise TypeError("instrument_type 必须是 InstrumentType 枚举或字符串")

    def set_name(self, name: str) -> None:
        """设置金融品种名称"""
        self.symbol = name

    def set_instrument_type(self, instrument_type: Union[InstrumentType, str]) -> None:
        """设置金融工具类型"""
        self.instrument_type = self._parse_instrument_type(instrument_type)

    def set_data_pd_dataframe(self, table: pd.DataFrame) -> None:
        """
        设置数据表并自动提取时间范围

        Args:
            table: 包含金融数据的DataFrame，必须有时间索引
        """
        if not isinstance(table, pd.DataFrame):
            raise TypeError("table必须是pandas DataFrame类型")

        if table.empty:
            raise ValueError("数据表不能为空")

        # 验证索引是否为时间类型
        if not isinstance(table.index, pd.DatetimeIndex):
            raise ValueError("数据表必须具有DatetimeIndex索引")

        self.table = table.copy()
        self._extract_time_range()
        self._data_loaded = True

    def _extract_time_range(self) -> None:
        """从数据表中提取时间范围"""
        if self.table is None or self.table.empty:
            self.start_time = None
            self.end_time = None
            return

        self.start_time = self.table.index[0].to_pydatetime()
        self.end_time = self.table.index[-1].to_pydatetime()

    def get_series(self, column: str) -> pd.Series:
        """
        获取指定列的数据序列

        Args:
            column: 列名

        Returns:
            pd.Series: 指定列的数据

        Raises:
            ValueError: 如果数据未加载或列不存在
        """
        if not self._data_loaded or self.table is None:
            raise ValueError("数据未加载，请先调用set_data_pd_dataframe()")

        if column not in self.table.columns:
            available_columns = list(self.table.columns)
            raise ValueError(f"列 '{column}' 不存在。可用列: {available_columns}")

        return self.table[column]

    # 常用列的便捷访问属性
    @property
    def open(self) -> pd.Series:
        """开盘价序列"""
        return self.get_series(self.OPEN)

    @property
    def high(self) -> pd.Series:
        """最高价序列"""
        return self.get_series(self.HIGH)

    @property
    def low(self) -> pd.Series:
        """最低价序列"""
        return self.get_series(self.LOW)

    @property
    def close(self) -> pd.Series:
        """收盘价序列"""
        return self.get_series(self.CLOSE)

    @property
    def volume(self) -> pd.Series:
        """成交量序列"""
        return self.get_series(self.VOLUME)

    def to_numpy(self, column: str) -> np.ndarray:
        """获取指定列的numpy数组"""
        return self.get_series(column).values

    def slice_time(self, start: Optional[Union[str, datetime]] = None,
                   end: Optional[Union[str, datetime]] = None) -> 'EData':
        """
        按时间范围切片数据

        Args:
            start: 开始时间
            end: 结束时间

        Returns:
            EData: 新的数据切片实例
        """
        if not self._data_loaded or self.table is None:
            raise ValueError("数据未加载，无法切片")

        sliced_table = self.table.loc[start:end]
        sliced_data = EData(self.symbol, self.instrument_type)
        sliced_data.set_data_pd_dataframe(sliced_table)

        # 复制期货特有属性
        if self.instrument_type == InstrumentType.FUTURE:
            sliced_data.multiplier = self.multiplier
            sliced_data.margin_rate = self.margin_rate
            sliced_data.commission_rate = self.commission_rate

        return sliced_data

    def get_data_info(self) -> dict:
        """获取数据基本信息"""
        if not self._data_loaded or self.table is None:
            return {"status": "数据未加载"}

        info = {
            "symbol": self.symbol,
            "instrument_type": self.instrument_type.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "data_points": len(self.table),
            "columns": list(self.table.columns),
            "data_types": self.table.dtypes.to_dict(),
            "memory_usage": f"{self.table.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        }

        # 添加期货特有信息
        if self.instrument_type == InstrumentType.FUTURE:
            info.update({
                "multiplier": self.multiplier,
                "margin_rate": self.margin_rate,
                "commission_rate": self.commission_rate
            })

        return info

    def add_column(self, column_name: str, data: Union[List, np.ndarray, pd.Series]) -> None:
        """添加新列到数据表"""
        if not self._data_loaded or self.table is None:
            raise ValueError("数据未加载，无法添加列")

        if len(data) != len(self.table):
            raise ValueError(f"数据长度不匹配: 现有{len(self.table)}行，新数据{len(data)}行")

        self.table[column_name] = data

    def rename_column(self, old_name: str, new_name: str) -> None:
        """重命名列"""
        if not self._data_loaded or self.table is None:
            raise ValueError("数据未加载，无法重命名列")

        if old_name not in self.table.columns:
            raise ValueError(f"列 '{old_name}' 不存在")

        self.table.rename(columns={old_name: new_name}, inplace=True)

    def drop_column(self, column_name: str) -> None:
        """删除指定列"""
        if not self._data_loaded or self.table is None:
            raise ValueError("数据未加载，无法删除列")

        if column_name not in self.table.columns:
            raise ValueError(f"列 '{column_name}' 不存在")

        # 防止删除必要的基础列
        essential_columns = [self.OPEN, self.HIGH, self.LOW, self.CLOSE]
        if column_name in essential_columns:
            raise ValueError(f"不能删除基础列: {column_name}")

        self.table.drop(columns=[column_name], inplace=True)

    def is_derivative(self) -> bool:
        """判断是否为衍生品"""
        derivative_types = [
            InstrumentType.FUTURE,
            InstrumentType.OPTION,
            InstrumentType.WARRANT,
            InstrumentType.SWAP,
            InstrumentType.STRUCTURED_PRODUCT
        ]
        return self.instrument_type in derivative_types

    def get_instrument_type_description(self) -> str:
        """获取金融工具类型描述"""
        descriptions = {
            InstrumentType.STOCK: "股票",
            InstrumentType.FUTURE: "期货",
            InstrumentType.OPTION: "期权",
            InstrumentType.INDEX: "指数",
            InstrumentType.ETF: "交易所交易基金",
            InstrumentType.FOREX: "外汇",
            InstrumentType.CRYPTO: "加密货币",
            InstrumentType.BOND: "债券",
            InstrumentType.COMMODITY: "商品",
            InstrumentType.WARRANT: "权证",
            InstrumentType.SWAP: "互换",
            InstrumentType.STRUCTURED_PRODUCT: "结构化产品",
            InstrumentType.MUTUAL_FUND: "共同基金"
        }
        return descriptions.get(self.instrument_type, "未知类型")

    def set_future_params(self, multiplier: float = 1.0, margin_rate: float = 0.1,
                          commission_rate: float = 0.0001) -> None:
        """
        设置期货参数

        Args:
            multiplier: 合约乘数
            margin_rate: 保证金比例
            commission_rate: 手续费率
        """
        if self.instrument_type != InstrumentType.FUTURE:
            warnings.warn("设置期货参数，但数据类型不是期货")

        self.multiplier = multiplier
        self.margin_rate = margin_rate
        self.commission_rate = commission_rate

    def __len__(self) -> int:
        """数据长度"""
        if not self._data_loaded or self.table is None:
            return 0
        return len(self.table)

    def __repr__(self) -> str:
        """字符串表示"""
        if not self._data_loaded:
            return f"EData('{self.symbol}', {self.instrument_type.value}) - 数据未加载"

        info = self.get_data_info()
        return (f"EData('{self.symbol}', {self.instrument_type.value}) - "
                f"时间范围: {self.start_time.strftime('%Y-%m-%d')} 至 {self.end_time.strftime('%Y-%m-%d')}, "
                f"数据点: {info['data_points']}, 列: {info['columns']}")

    def __getitem__(self, column: str) -> pd.Series:
        """支持字典式访问列数据"""
        return self.get_series(column)


class OrderType(Enum):
    """订单类型枚举"""
    MARKET = "market"  # 市价单
    LIMIT = "limit"  # 限价单
    STOP = "stop"  # 止损单


class OrderDirection(Enum):
    """订单方向枚举"""
    BUY = "buy"  # 买入
    SELL = "sell"  # 卖出
    SHORT = "short"  # 做空


class Trade:
    """交易记录类"""

    def __init__(self, symbol: str, direction: OrderDirection, quantity: float,
                 price: float, timestamp: datetime, commission: float = 0.0):
        self.symbol = symbol
        self.direction = direction
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp
        self.commission = commission
        self.value = quantity * price
        self.net_value = self.value - commission if direction == OrderDirection.BUY else self.value + commission

    def __repr__(self):
        return f"Trade({self.symbol}, {self.direction.value}, {self.quantity}, {self.price:.2f})"


class Position:
    """持仓类"""

    def __init__(self, symbol: str, instrument_type: InstrumentType = InstrumentType.STOCK):
        self.symbol = symbol
        self.instrument_type = instrument_type
        self.quantity = 0.0
        self.avg_price = 0.0
        self.realized_pnl = 0.0  # 已实现盈亏
        self.unrealized_pnl = 0.0  # 未实现盈亏
        self.total_investment = 0.0  # 总投入
        self.margin_used = 0.0  # 保证金占用（期货）

    def update(self, price: float, multiplier: float = 1.0):
        """更新未实现盈亏"""
        if self.quantity > 0:
            self.unrealized_pnl = (price - self.avg_price) * self.quantity * multiplier
        elif self.quantity < 0:
            self.unrealized_pnl = (self.avg_price - price) * abs(self.quantity) * multiplier
        else:
            self.unrealized_pnl = 0.0

    def update_margin(self, price: float, margin_rate: float, multiplier: float = 1.0):
        """更新保证金占用（期货）"""
        if self.quantity != 0:
            self.margin_used = abs(self.quantity) * price * margin_rate * multiplier
        else:
            self.margin_used = 0.0

    def __repr__(self):
        return f"Position({self.symbol}, {self.quantity}, avg_price={self.avg_price:.2f})"


class CommissionModel:
    """手续费模型基类"""

    def calculate(self, trade: Trade, data: EData) -> float:
        """
        计算交易手续费

        Args:
            trade: 交易记录
            data: 对应的EData对象

        Returns:
            float: 手续费金额
        """
        return 0.0


class FixedCommissionModel(CommissionModel):
    """固定比例手续费模型"""

    def __init__(self, rate: float = 0.0003, min_commission: float = 5.0):
        """
        Args:
            rate: 手续费率，默认万分之三
            min_commission: 最低手续费，默认5元
        """
        self.rate = rate
        self.min_commission = min_commission

    def calculate(self, trade: Trade, data: EData) -> float:
        # 期货使用其特定的手续费率
        if data.instrument_type == InstrumentType.FUTURE:
            rate = data.commission_rate
            commission = trade.value * rate
            return commission
        else:
            commission = trade.value * self.rate
            return max(commission, self.min_commission)


class SlippageModel:
    """滑点模型基类"""

    def apply(self, price: float, direction: OrderDirection) -> float:
        """
        应用滑点到价格

        Args:
            price: 原始价格
            direction: 交易方向

        Returns:
            float: 应用滑点后的价格
        """
        return price


class FixedSlippageModel(SlippageModel):
    """固定滑点模型"""

    def __init__(self, slippage: float = 0.001):
        """
        Args:
            slippage: 滑点比例，默认千分之一
        """
        self.slippage = slippage

    def apply(self, price: float, direction: OrderDirection) -> float:
        if direction == OrderDirection.BUY:
            return price * (1 + self.slippage)
        else:  # SELL or SHORT
            return price * (1 - self.slippage)


class Analyzer:
    """分析器基类"""

    def __init__(self):
        self.results = {}

    def calculate(self, engine: 'Engine') -> Dict[str, Any]:
        """计算分析指标"""
        return {}


class PerformanceAnalyzer(Analyzer):
    """性能分析器"""

    def calculate(self, engine: 'Engine') -> Dict[str, Any]:
        """计算性能指标"""
        if not engine.portfolio_history:
            return {}

        # 提取组合价值序列
        portfolio_values = [record['portfolio_value'] for record in engine.portfolio_history]
        dates = [record['date'] for record in engine.portfolio_history]

        # 计算收益率序列
        returns = []
        for i in range(1, len(portfolio_values)):
            ret = (portfolio_values[i] - portfolio_values[i - 1]) / portfolio_values[i - 1]
            returns.append(ret)

        returns = np.array(returns)

        # 总收益率
        total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]

        # 年化收益率
        trading_days = len(portfolio_values)
        if trading_days > 1:
            years = (dates[-1] - dates[0]).days / 365.0
            annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        else:
            annual_return = 0

        # 年化波动率
        if len(returns) > 0:
            annual_volatility = np.std(returns) * np.sqrt(252)
        else:
            annual_volatility = 0

        # 夏普比率（假设无风险利率为0）
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0

        # 最大回撤
        max_drawdown = self._calculate_max_drawdown(portfolio_values)

        # Calmar比率
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0

        # 胜率
        win_rate = self._calculate_win_rate(engine.trades)

        # 盈亏比
        profit_factor = self._calculate_profit_factor(engine.trades)

        return {
            '总收益率': total_return,
            '年化收益率': annual_return,
            '年化波动率': annual_volatility,
            '夏普比率': sharpe_ratio,
            '最大回撤': max_drawdown,
            'Calmar比率': calmar_ratio,
            '总交易次数': len(engine.trades),
            '胜率': win_rate,
            '盈亏比': profit_factor,
            '最终组合价值': portfolio_values[-1],
            '最终现金': engine.cash
        }

    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """计算最大回撤"""
        peak = portfolio_values[0]
        max_dd = 0.0

        for value in portfolio_values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_win_rate(self, trades: List[Trade]) -> float:
        """计算胜率"""
        if not trades:
            return 0.0

        # 简化计算，实际应用中需要根据持仓和价格变化判断每笔交易是否盈利
        # 这里我们假设无法直接判断，返回0
        return 0.0

    def _calculate_profit_factor(self, trades: List[Trade]) -> float:
        """计算盈亏比"""
        if not trades:
            return 0.0

        # 简化计算，实际应用中需要根据持仓和价格变化判断每笔交易的盈亏
        # 这里我们假设无法直接计算，返回0
        return 0.0


class Engine(ABC):
    """
    回测引擎基类
    管理数据、交易成本、账户状态，提供高度自由度的策略定制接口
    """

    def __init__(self, initial_cash: float = 1000000.0):
        """
        初始化回测引擎

        Args:
            initial_cash: 初始资金
        """
        # 数据管理
        self.data: Dict[str, EData] = {}  # 所有数据
        self.current_data: Dict[str, EData] = {}  # 当前可用数据（已切片到当前时间）

        # 时间管理
        self.start_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None
        self.current_date: Optional[datetime] = None
        self.date_index: int = 0

        # 账户状态
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.portfolio_value = initial_cash
        self.available_margin = initial_cash  # 可用保证金（期货）

        # 交易成本模型
        self.commission_model: CommissionModel = FixedCommissionModel()
        self.slippage_model: SlippageModel = FixedSlippageModel()

        # 印花税（仅适用于A股卖出）
        self.stamp_tax_rate = 0.001  # 千分之一

        # 回测状态
        self.is_running = False
        self.daily_returns: List[float] = []
        self.portfolio_history: List[Dict[str, Any]] = []

        # 分析器
        self.analyzers: List[Analyzer] = [PerformanceAnalyzer()]

    def add_data(self, symbol: str, data: EData) -> None:
        """
        添加金融数据

        Args:
            symbol: 品种代码
            data: EData实例
        """
        self.data[symbol] = data

        # 自动设置回测时间范围
        if self.start_date is None or data.start_time > self.start_date:
            self.start_date = data.start_time
        if self.end_date is None or data.end_time < self.end_date:
            self.end_date = data.end_time

    def set_commission_model(self, model: CommissionModel) -> None:
        """设置手续费模型"""
        self.commission_model = model

    def set_slippage_model(self, model: SlippageModel) -> None:
        """设置滑点模型"""
        self.slippage_model = model

    def set_stamp_tax_rate(self, rate: float) -> None:
        """设置印花税率"""
        self.stamp_tax_rate = rate

    def add_analyzer(self, analyzer: Analyzer) -> None:
        """添加分析器"""
        self.analyzers.append(analyzer)

    def get_current_price(self, symbol: str, price_type: str = 'close') -> float:
        """
        获取当前价格

        Args:
            symbol: 品种代码
            price_type: 价格类型 ('open', 'high', 'low', 'close')

        Returns:
            float: 当前价格
        """
        if symbol not in self.current_data:
            raise ValueError(f"品种 {symbol} 的数据未加载或当前不可用")

        data = self.current_data[symbol]
        price_series = data.get_series(price_type)

        # 获取当前日期对应的价格
        if self.current_date in price_series.index:
            return float(price_series.loc[self.current_date])
        else:
            # 如果当前日期没有数据，使用最新可用数据
            available_dates = price_series.index[price_series.index <= self.current_date]
            if len(available_dates) > 0:
                latest_date = available_dates[-1]
                return float(price_series.loc[latest_date])
            else:
                raise ValueError(f"无法获取 {symbol} 在 {self.current_date} 的价格")

    def get_historical_data(self, symbol: str, lookback: int = 1) -> EData:
        """
        获取历史数据

        Args:
            symbol: 品种代码
            lookback: 回溯天数

        Returns:
            EData: 历史数据切片
        """
        if symbol not in self.data:
            raise ValueError(f"品种 {symbol} 的数据未加载")

        end_date = self.current_date
        start_date = end_date - timedelta(days=lookback)

        return self.data[symbol].slice_time(start_date, end_date)

    def get_position(self, symbol: str) -> Position:
        """
        获取持仓信息

        Args:
            symbol: 品种代码

        Returns:
            Position: 持仓对象
        """
        if symbol not in self.positions:
            instrument_type = self.data[symbol].instrument_type
            self.positions[symbol] = Position(symbol, instrument_type)
        return self.positions[symbol]

    def order(self, symbol: str, direction: OrderDirection, quantity: float,
              order_type: OrderType = OrderType.MARKET, limit_price: Optional[float] = None) -> bool:
        """
        下单交易

        Args:
            symbol: 品种代码
            direction: 交易方向
            quantity: 数量
            order_type: 订单类型
            limit_price: 限价单价格

        Returns:
            bool: 是否成交
        """
        if quantity <= 0:
            raise ValueError("交易数量必须大于0")

        # 获取当前价格
        if order_type == OrderType.MARKET:
            price = self.get_current_price(symbol)
        elif order_type == OrderType.LIMIT and limit_price is not None:
            price = limit_price
        else:
            raise ValueError("限价单必须指定限价")

        # 应用滑点
        executed_price = self.slippage_model.apply(price, direction)

        # 获取数据对象
        data = self.data[symbol]

        # 计算交易金额
        multiplier = data.multiplier if data.instrument_type == InstrumentType.FUTURE else 1.0
        trade_value = quantity * executed_price * multiplier

        # 计算保证金要求（期货）
        margin_required = 0.0
        if data.instrument_type == InstrumentType.FUTURE:
            margin_required = quantity * executed_price * data.margin_rate * multiplier

        # 检查资金是否足够
        if direction == OrderDirection.BUY:
            if data.instrument_type == InstrumentType.FUTURE:
                # 期货买入：检查保证金是否足够
                if margin_required > self.available_margin:
                    print(f"保证金不足: 需要 {margin_required}, 可用 {self.available_margin}")
                    return False
            else:
                # 股票买入：检查现金是否足够
                if trade_value > self.cash:
                    print(f"资金不足: 需要 {trade_value}, 可用 {self.cash}")
                    return False
        elif direction == OrderDirection.SHORT:
            # 期货卖空：检查保证金是否足够
            if data.instrument_type != InstrumentType.FUTURE:
                print("非期货品种不能做空")
                return False

            if margin_required > self.available_margin:
                print(f"保证金不足: 需要 {margin_required}, 可用 {self.available_margin}")
                return False

        # 创建交易记录
        trade = Trade(symbol, direction, quantity, executed_price, self.current_date)
        commission = self.commission_model.calculate(trade, data)
        trade.commission = commission

        # 计算印花税（仅卖出A股时）
        stamp_tax = 0.0
        if direction == OrderDirection.SELL and self._is_a_stock(symbol):
            stamp_tax = trade_value * self.stamp_tax_rate

        total_cost = commission + stamp_tax

        # 更新现金和保证金
        if direction == OrderDirection.BUY:
            if data.instrument_type == InstrumentType.FUTURE:
                # 期货买入：扣除保证金
                self.available_margin -= margin_required
            else:
                # 股票买入：扣除现金
                self.cash -= (trade_value + total_cost)
        elif direction == OrderDirection.SELL:
            if data.instrument_type == InstrumentType.FUTURE:
                # 期货平多：释放保证金
                position = self.get_position(symbol)
                if position.quantity > 0:
                    released_margin = min(quantity,
                                          position.quantity) * position.avg_price * data.margin_rate * multiplier
                    self.available_margin += released_margin
            else:
                # 股票卖出：增加现金
                self.cash += (trade_value - total_cost)
        elif direction == OrderDirection.SHORT:
            # 期货卖空：扣除保证金
            self.available_margin -= margin_required

        # 更新持仓
        position = self.get_position(symbol)
        if direction == OrderDirection.BUY:
            new_quantity = position.quantity + quantity
            if new_quantity != 0:
                position.avg_price = (position.avg_price * position.quantity + executed_price * quantity) / new_quantity
            position.quantity = new_quantity
            position.total_investment += trade_value

            # 更新保证金占用（期货）
            if data.instrument_type == InstrumentType.FUTURE:
                position.update_margin(executed_price, data.margin_rate, data.multiplier)

        elif direction == OrderDirection.SELL:
            if position.quantity < quantity:
                print(f"持仓不足: 持有 {position.quantity}, 尝试卖出 {quantity}")
                return False

            # 计算已实现盈亏
            realized_pnl = (executed_price - position.avg_price) * quantity * multiplier
            position.realized_pnl += realized_pnl
            position.quantity -= quantity
            position.total_investment -= position.avg_price * quantity * multiplier

            # 更新保证金占用（期货）
            if data.instrument_type == InstrumentType.FUTURE:
                position.update_margin(executed_price, data.margin_rate, data.multiplier)

        elif direction == OrderDirection.SHORT:
            new_quantity = position.quantity - quantity
            if new_quantity != 0:
                # 对于空头持仓，平均价格计算方式不同
                if position.quantity == 0:
                    position.avg_price = executed_price
                else:
                    total_value = abs(position.quantity) * position.avg_price + quantity * executed_price
                    position.avg_price = total_value / abs(new_quantity)
            position.quantity = new_quantity

            # 更新保证金占用（期货）
            if data.instrument_type == InstrumentType.FUTURE:
                position.update_margin(executed_price, data.margin_rate, data.multiplier)

        # 记录交易
        self.trades.append(trade)

        # 更新持仓的未实现盈亏
        position.update(executed_price, multiplier)

        return True

    def _is_a_stock(self, symbol: str) -> bool:
        """
        判断是否为A股（简单实现）

        Args:
            symbol: 品种代码

        Returns:
            bool: 是否为A股
        """
        # 这里可以根据实际情况实现更复杂的判断逻辑
        return symbol.endswith('.SZ') or symbol.endswith('.SH')

    def update_portfolio_value(self) -> None:
        """更新组合价值"""
        portfolio_value = self.cash + self.available_margin

        for symbol, position in self.positions.items():
            if position.quantity != 0:
                data = self.data[symbol]
                current_price = self.get_current_price(symbol)
                multiplier = data.multiplier if data.instrument_type == InstrumentType.FUTURE else 1.0

                position.update(current_price, multiplier)

                if data.instrument_type == InstrumentType.FUTURE:
                    # 期货：组合价值 = 现金 + 保证金 + 未实现盈亏
                    portfolio_value += position.unrealized_pnl
                else:
                    # 股票：组合价值 = 现金 + 持仓市值
                    portfolio_value += position.quantity * current_price

        self.portfolio_value = portfolio_value

    def run_backtest(self) -> None:
        """
        运行回测
        """
        if not self.data:
            raise ValueError("没有加载任何数据")

        if self.start_date is None or self.end_date is None:
            raise ValueError("未设置回测时间范围")

        self.is_running = True

        # 生成回测日期序列
        all_dates = []
        for symbol, data in self.data.items():
            all_dates.extend(data.table.index.tolist())

        # 去重并排序
        unique_dates = sorted(set(all_dates))
        unique_dates = [date for date in unique_dates if self.start_date <= date <= self.end_date]

        # 初始化
        self.daily_returns = []
        self.portfolio_history = []

        # 逐日回测
        for self.date_index, date in enumerate(unique_dates):
            self.current_date = date

            # 更新当前可用数据（切片到当前日期）
            for symbol, data in self.data.items():
                self.current_data[symbol] = data.slice_time(end=date)

            # 调用用户定义的策略逻辑
            self.roll()

            # 更新组合价值
            previous_value = self.portfolio_value
            self.update_portfolio_value()

            # 计算日收益率
            if previous_value > 0:
                daily_return = (self.portfolio_value - previous_value) / previous_value
                self.daily_returns.append(daily_return)
            else:
                self.daily_returns.append(0.0)

            # 记录组合状态
            self.portfolio_history.append({
                'date': date,
                'portfolio_value': self.portfolio_value,
                'cash': self.cash,
                'available_margin': self.available_margin,
                'positions': {sym: (pos.quantity, pos.avg_price) for sym, pos in self.positions.items() if
                              pos.quantity != 0}
            })

        self.is_running = False

    @abstractmethod
    def roll(self) -> None:
        """
        每个时间步调用的策略逻辑
        用户需要重写此方法来实现自己的交易策略
        """
        pass

    def get_analysis(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有分析器的结果

        Returns:
            Dict[str, Dict[str, Any]]: 分析结果字典
        """
        results = {}
        for analyzer in self.analyzers:
            name = analyzer.__class__.__name__
            results[name] = analyzer.calculate(self)

        return results


# 示例策略实现
class MyStrategy(Engine):
    """示例策略：双均线策略"""

    def __init__(self, initial_cash: float = 1000000.0):
        super().__init__(initial_cash)
        self.sma_short = 20
        self.sma_long = 50

    def roll(self) -> None:
        """双均线策略逻辑"""
        # 获取当前数据
        symbol = "AAPL"  # 假设我们交易苹果股票

        if symbol not in self.data:
            return

        # 获取历史数据计算指标
        historical_data = self.get_historical_data(symbol, lookback=100)
        close_prices = historical_data.close

        # 计算技术指标
        sma_short = Indicators.sma(close_prices, self.sma_short)
        sma_long = Indicators.sma(close_prices, self.sma_long)

        # 确保有足够的数据计算指标
        if len(sma_short) < 1 or len(sma_long) < 1:
            return

        sma_short_val = sma_short[-1]
        sma_long_val = sma_long[-1]

        # 获取当前价格
        current_price = self.get_current_price(symbol)

        # 获取当前持仓
        position = self.get_position(symbol)

        # 策略逻辑：双均线金叉死叉
        if sma_short_val > sma_long_val and position.quantity <= 0:
            # 金叉信号，买入
            if self.data[symbol].instrument_type == InstrumentType.FUTURE:
                # 期货：使用部分保证金
                quantity = int(self.available_margin * 0.1 / (current_price * self.data[symbol].margin_rate))
            else:
                # 股票：使用10%资金
                quantity = int(self.cash * 0.1 / current_price)

            if quantity > 0:
                self.order(symbol, OrderDirection.BUY, quantity)

        elif sma_short_val < sma_long_val and position.quantity > 0:
            # 死叉信号，卖出
            self.order(symbol, OrderDirection.SELL, position.quantity)


# 使用示例
if __name__ == "__main__":
    # 创建策略实例
    strategy = MyStrategy(initial_cash=1000000)

    # 创建股票数据
    stock_data = EData("AAPL", InstrumentType.STOCK)
    # 假设已经设置了数据
    # stock_data.set_data_pd_dataframe(...)

    # 创建期货数据
    future_data = EData("CL2024", InstrumentType.FUTURE)
    future_data.set_future_params(multiplier=1000, margin_rate=0.1, commission_rate=0.0001)
    # 假设已经设置了数据
    # future_data.set_data_pd_dataframe(...)

    # 添加数据到策略
    strategy.add_data("AAPL", stock_data)
    strategy.add_data("CL2024", future_data)

    # 设置交易成本
    strategy.set_commission_model(FixedCommissionModel(rate=0.0003))
    strategy.set_slippage_model(FixedSlippageModel(slippage=0.001))

    # 运行回测
    strategy.run_backtest()

    # 获取分析结果
    analysis = strategy.get_analysis()
    print("回测分析结果:")
    for analyzer_name, result in analysis.items():
        print(f"\n{analyzer_name}:")
        for key, value in result.items():
            print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")