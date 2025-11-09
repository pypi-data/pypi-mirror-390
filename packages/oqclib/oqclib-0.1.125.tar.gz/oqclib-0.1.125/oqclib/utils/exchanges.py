from typing import Optional, Dict


# 定义一些常量类（代替 Java 的 enum）
class ExchangeType:
    CEX = "CEX"
    DEX = "DEX"


class AmendType:
    NotAllowed = "NotAllowed"
    Native = "Native"
    Simulated = "Simulated"


class Chains:
    ETH = "ETH"
    OKBC = "OKBC"
    BSC = "BSC"


class Exchange:
    def __init__(self, name: str, short_name: str, exchange_type: str, amend_type: str, chain: Optional[str] = None):
        self.name = name
        self.short_name = short_name
        self.exchange_type = exchange_type
        self.amend_type = amend_type
        self.chain = chain

    def __eq__(self, other):
        return self.name == other.name and self.short_name == other.short_name

    def __repr__(self):
        return f"Exchange(name={self.name}, short_name={self.short_name})"


__EXCHANGE_LIST = [
    Exchange("BINANCE", "BN", ExchangeType.CEX, AmendType.NotAllowed),
    Exchange("OKX", "OK", ExchangeType.CEX, AmendType.NotAllowed),
    Exchange("GATE", "GT", ExchangeType.CEX, AmendType.NotAllowed),
    Exchange("BITGET", "BG", ExchangeType.CEX, AmendType.NotAllowed),
    Exchange("BYBIT", "BB", ExchangeType.CEX, AmendType.NotAllowed)
]

__EXCHANGE_LIST_BY_SHORT_NAME = {exch.short_name: exch for exch in __EXCHANGE_LIST}
__EXCHANGE_LIST_BY_NAME = {exch.name: exch for exch in __EXCHANGE_LIST}


def get_exchange_by_name(name: str) -> Optional[Exchange]:
    return __EXCHANGE_LIST_BY_NAME.get(name)


def get_exchange_by_short_name(short_name: str) -> Optional[Exchange]:
    return __EXCHANGE_LIST_BY_SHORT_NAME.get(short_name)


class Exchanges:
    pass


for exch in __EXCHANGE_LIST:
    setattr(Exchanges, exch.name, exch)
