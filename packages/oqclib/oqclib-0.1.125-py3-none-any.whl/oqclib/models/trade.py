from enum import Enum


class TradingSide(Enum):
    BUY = 1,
    SELL = -1,
    BIDIR = 0
