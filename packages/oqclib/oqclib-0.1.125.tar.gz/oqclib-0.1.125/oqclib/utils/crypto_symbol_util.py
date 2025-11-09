from typing import Optional

from oqclib.utils.exchanges import Exchange, get_exchange_by_short_name


def jtp_symbol_to_ccxt_symbol_for_bitget(jtp_symbol_no_exch):
    parts = jtp_symbol_no_exch.split('-')
    coin = parts[0]
    quote_ccy = parts[1]

    if quote_ccy == 'USDT':
        return f"{coin}/{quote_ccy}:{quote_ccy}"
    elif quote_ccy == 'USDC':
        return f"{coin}/{quote_ccy}:{quote_ccy}"
    return jtp_symbol_no_exch

def jtp_symbol_to_ccxt_symbol_for_binance(jtp_symbol_no_exch):
    parts = jtp_symbol_no_exch.split('-')
    coin = parts[0]
    quote_ccy = parts[1]

    if quote_ccy == 'USDT':
        return f"{coin}/{quote_ccy}:{quote_ccy}"
    elif quote_ccy == 'USDC':
        return f"{coin}/{quote_ccy}:{quote_ccy}"
    return jtp_symbol_no_exch

def jtp_symbol_to_ccxt_symbol_for_bybit(jtp_symbol_no_exch):
    parts = jtp_symbol_no_exch.split('-')
    coin = parts[0]
    quote_ccy = parts[1]

    if quote_ccy == 'USDT':
        return f"{coin}/{quote_ccy}:{quote_ccy}"
    elif quote_ccy == 'USDC':
        return f"{coin}/{quote_ccy}:{quote_ccy}"
    return jtp_symbol_no_exch


def jtp_symbol_to_ccxt_symbol(symbol: str) -> str:
    parts = symbol.split('.')
    symbol_without_exch = parts[0]
    if parts[1] == 'OK':
        return symbol_without_exch
    if parts[1] == 'BN':
        return jtp_symbol_to_ccxt_symbol_for_binance(symbol_without_exch)
    if parts[1] == 'BG':
        return jtp_symbol_to_ccxt_symbol_for_bitget(symbol_without_exch)
    if parts[1] == 'BB':
        return jtp_symbol_to_ccxt_symbol_for_bybit(symbol_without_exch)
    return symbol


def get_coin_and_quote_ccy_from_jtp_symbol(symbol: str) -> (str, str):
    parts = symbol.split('.')
    if len(parts) < 2:
        return None, None
    parts = parts[0].split('-')
    if len(parts) < 2:
        return None, None
    coin = parts[0]
    quote_ccy = parts[1]
    return coin, quote_ccy


def get_exchange_from_jtp_symbol(symbol: str) -> Optional[Exchange]:
    parts = symbol.split('.')
    exchange_short_name = parts[1]
    return get_exchange_by_short_name(exchange_short_name)


def get_exchange_url_for_perpetual(exchange_name: str, coin: str, quote_ccy: str) -> str:
    exchange_name = exchange_name.lower()
    if exchange_name == 'binance':  
        return f'https://www.binance.com/futures/{coin.upper()}{quote_ccy.upper()}'
    elif exchange_name == 'bitget':
        return f'https://www.bitget.com/futures/{quote_ccy.lower()}/{coin.upper()}{quote_ccy.upper()}'
    elif exchange_name == 'bybit':
        return f'https://www.bybit.com/trade/{quote_ccy.lower()}/{coin.upper()}{quote_ccy.upper()}'
    elif exchange_name == 'hyperliquid':
        return f'https://www.hyperliquid.xyz/trade/{coin.upper()}'
    elif exchange_name == 'okx':
        return f'https://www.okx.com/trade-swap/{coin.lower()}-{quote_ccy.lower()}-swap'
    return ''

def get_exchange_url_from_jtp_symbol(jtp_symbol: str) -> str:
    exchange = get_exchange_from_jtp_symbol(jtp_symbol)
    coin, quote_ccy = get_coin_and_quote_ccy_from_jtp_symbol(jtp_symbol)
    url = get_exchange_url_for_perpetual(exchange.name, coin, quote_ccy)
    return url

def get_coin_and_quote_ccy_from_ccxt_symbol(exchange_name: str, symbol: str) -> (str, str):
    if exchange_name == 'binance':
        return get_coin_and_quote_ccy_from_binance_ccxt_symbol(symbol)
    if exchange_name == 'okx':
        return get_coin_and_quote_ccy_from_okx_ccxt_symbol(symbol)
    return None, None

def get_coin_and_quote_ccy_from_binance_ccxt_symbol(symbol: str) -> (str, str):
    # Handle both formats: "BNB/USDT" and "BNB/USDT:USDT"
    if ':' in symbol:
        symbol = symbol.split(':')[0]
    parts = symbol.split('/')
    if len(parts) != 2:
        return None, None
    return parts[0], parts[1]

def get_coin_and_quote_ccy_from_okx_ccxt_symbol(symbol: str) -> (str, str):
    parts = symbol.split('-')
    if len(parts) < 2:
        return None, None
    return parts[0], parts[1]

