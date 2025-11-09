import pandas as pd

def to_tushare_date_str(date: pd.Timestamp) -> str:
    return str(date.date()).replace("-","")