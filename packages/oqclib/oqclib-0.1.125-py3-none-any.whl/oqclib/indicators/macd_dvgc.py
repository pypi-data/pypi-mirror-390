from __future__ import annotations

import pandas as pd
from .model import DivergenceType
import logging

logger = logging.getLogger(__name__)

FIELD = 'dif'
CROSS_THRESHOLD = 2


def populate_macd_fields(df: pd.DataFrame, fast_period=12, slow_period=26, signal_period=9, ma_type='ema'):
    """
    Calculate MACD fields using either EMA or SMA
    Args:
        df: DataFrame with 'close' column
        fast_period: period for fast moving average
        slow_period: period for slow moving average
        signal_period: period for signal line
        ma_type: moving average type ('ema' or 'sma')
    """
    if ma_type.lower() == 'ema':
        df['ema_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
        df['dif'] = df['ema_fast'] - df['ema_slow']
        df['dea'] = df['dif'].ewm(span=signal_period, adjust=False).mean()
    elif ma_type.lower() == 'sma':
        df['ema_fast'] = df['close'].rolling(window=fast_period).mean()
        df['ema_slow'] = df['close'].rolling(window=slow_period).mean()
        df['dif'] = df['ema_fast'] - df['ema_slow']
        df['dea'] = df['dif'].rolling(window=signal_period).mean()
    else:
        raise ValueError("ma_type must be either 'ema' or 'sma'")


def detect_macd_divergence(df: pd.DataFrame, nth: int = 0) -> DivergenceType | None:
    assert 'close' in df.columns, "Dataframe must contain 'close' column"
    assert 'dif' in df.columns, "Dataframe must contain 'ema12' column"
    assert 'dea' in df.columns, "Dataframe must contain 'ema26' column"

    ret = is_bearish_divergence(df, nth)
    if ret is not None:
        logger.info(
            f"Bearish divergence detected {df.loc[ret[0]][['close', 'dif', 'dea']]} {df.loc[ret[1]][['close', 'dif', 'dea']]} last {df.tail(5)[['close', 'dif', 'dea']]}")
        return DivergenceType.BEARISH
    ret = is_bullish_divergence(df, nth)
    if ret is not None:
        logger.info(
            f"Bullish divergence detected {df.loc[ret[0]][['close', 'dif', 'dea']]} {df.loc[ret[1]][['close', 'dif', 'dea']]} last {df.tail(5)[['close', 'dif', 'dea']]}")
        return DivergenceType.BULLISH
    return None


def is_golden_cross(df: pd.DataFrame, nth: int = 0) -> bool:
    # time_ms = df.iloc[-nth - 1]['timeMs']
    # print(f"is_golden_cross, nth  {nth}, time: {time_ms}")
    dif_pre = df['dif'].iloc[-nth - 2]
    dea_pre = df['dea'].iloc[-nth - 2]
    return dif_pre < dea_pre and df['dif'].iloc[-nth - 1] > df['dea'].iloc[-nth - 1]


# Write is_death_cross function
def is_death_cross(df: pd.DataFrame, nth: int = 0) -> bool:
    return df['dif'].iloc[-nth - 2] > df['dea'].iloc[-nth - 2] and df['dif'].iloc[-nth - 1] < df['dea'].iloc[-nth - 1]


def is_bearish_divergence(df: pd.DataFrame, nth: int = 0) -> ():
    ret = None
    # 如果不是死叉，直接退出
    if not is_death_cross(df, nth):
        return None
    step = 1
    size = len(df)
    start1, start2, end1, end2 = 0, 0, 0, 0
    for i in range(nth + 1, size - 2):
        # 找到上一个金叉
        if step == 1 and is_golden_cross(df, nth=i):
            start1, end1 = nth + 1, i
            if end1 - start1 < CROSS_THRESHOLD:
                # print(f"First golden cross at {start1} {end1}")
                return ret
            step = 2
        # 找到上一个死叉
        if step == 2 and is_death_cross(df, nth=i):
            start2 = i + 1
            if start2 - end1 < CROSS_THRESHOLD:
                # print(f"First death cross at {end1} {start2}")
                return ret
            step = 3
        # 再找到上一个金叉
        if step == 3 and is_golden_cross(df, nth=i):
            end2 = i
            step = 4
            break
    if step == 4:
        # 求两个区间的最高价
        max1 = -1e8
        max2 = -1e8
        id1 = 0
        id2 = 0
        for i in range(start1, end1 + 1):
            if max1 < df[FIELD].iloc[-i - 1]:
                max1 = df[FIELD].iloc[-i - 1]
                id1 = i
        for i in range(start2, end2 + 1):
            if max2 < df[FIELD].iloc[-i - 1]:
                max2 = df[FIELD].iloc[-i - 1]
                id2 = i
        close1 = df['close'].iloc[-id1 - 1]
        close2 = df['close'].iloc[-id2 - 1]
        dif1 = df['dif'].iloc[-id1 - 1]
        dif2 = df['dif'].iloc[-id2 - 1]

        if close1 > close2 and dif1 < dif2:
            logger.info(f"Bearish divergence close2 {close2} dif2 {dif2} close1 {close1} dif1 {dif1}")
            ret = (df.index[-id2 - 1], df.index[-id1 - 1])
    return ret


def is_bullish_divergence(df: pd.DataFrame, nth: int = 0) -> ():
    ret = None
    # 如果不是金叉，直接退出
    if not is_golden_cross(df, nth=nth):
        return ret
    step = 1
    size = len(df)
    start1, start2, end1, end2 = 0, 0, 0, 0
    for i in range(nth + 1, size - 2):
        # 找到上一个死叉
        if step == 1 and is_death_cross(df, nth=i):
            start1, end1 = nth + 1, i
            if end1 - start1 < CROSS_THRESHOLD:
                # print(f"First death cross at {start1} {end1}")
                return ret
            step = 2
        # 找到上一个金叉
        if step == 2 and is_golden_cross(df, nth=i):
            start2 = i + 1
            if start2 - end1 < CROSS_THRESHOLD:
                # print(f"First Golden cross at {end1} {start2}")
                return ret
            step = 3
        # 再找到上一个死叉
        if step == 3 and is_death_cross(df, nth=i):
            end2 = i
            step = 4
            break
    if step == 4:
        # 求两个区间的最低价
        min1 = 1e8
        min2 = 1e8
        id1 = 0
        id2 = 0
        for i in range(start1, end1 + 1):
            if min1 > df[FIELD].iloc[-i - 1]:
                min1 = df[FIELD].iloc[-i - 1]
                id1 = i
        for i in range(start2, end2 + 1):
            if min2 > df[FIELD].iloc[-i - 1]:
                min2 = df[FIELD].iloc[-i - 1]
                id2 = i
        close1 = df['close'].iloc[-id1 - 1]
        close2 = df['close'].iloc[-id2 - 1]
        dif1 = df['dif'].iloc[-id1 - 1]
        dif2 = df['dif'].iloc[-id2 - 1]

        if close1 < close2 and dif1 > dif2:
            logger.info(f"Bullish divergence close2 {close2} dif2 {dif2} close1 {close1} dif1 {dif1}")
            ret = (df.index[-id2 - 1], df.index[-id1 - 1])
    return ret
