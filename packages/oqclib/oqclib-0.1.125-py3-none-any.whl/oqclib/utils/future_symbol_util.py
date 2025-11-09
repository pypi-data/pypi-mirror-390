
from datetime import datetime, date, timedelta
from .datetime_util import get_monthly_third_friday

def get_contract_time_of_next_n_month(year, month, n):
    month += n
    while month > 12:
        month -= 12
        year += 1
    return str(year % 100) + "%02d" % month


def get_future_symbol_root(spot):
    if spot == "sh000300":
        return "IF"
    if spot == "sh000905":
        return "IC"
    if spot == "sh000852":
        return "IM"
    if spot == "sh000016":
        return "IH"
    return None

def get_main_index_future_symbol(product: str, date: datetime.date):
    """
    根据传入日期，返回中国金融期货交易所指数期货主力合约
    
    规则：
    - 每月第三个星期五之前（不包括第三个星期五），返回当月合约
    - 每月第三个星期五以及之后，返回下月合约
    
    参数:
        product: 产品类型，如 'IF', 'IC', 'IM', 'IH'
        date: 日期对象
    
    返回:
        主力合约代码，如 'IF2309'
    """
    
    # 检查产品类型是否有效
    valid_products = ['IF', 'IC', 'IM', 'IH']
    if product not in valid_products:
        raise ValueError(f"无效的产品类型: {product}，有效类型为: {valid_products}")
    
    year = date.year
    month = date.month
    
    # 计算当月交割日
    delivery_day = get_monthly_third_friday(year, month)
    
    # 判断返回当月合约还是下月合约
    if date < delivery_day:
        # 当月合约
        contract_month = get_contract_time_of_next_n_month(year, month, 0)
    else:
        # 下月合约
        contract_month = get_contract_time_of_next_n_month(year, month, 1)
    
    # 组合合约代码
    main_contract = f"{product}{contract_month}"
    return main_contract

if __name__ == '__main__':
    print(get_main_index_future_symbol('IF', date(year=2025, month=9, day=18)))
