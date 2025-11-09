import math
from datetime import datetime, timedelta, date

YYYYMMDD_HHMMSS = "%Y%m%d_%H%M%S"

def seconds_to_next_interval(dt: datetime, interval_seconds: int) -> float:
    # Calculate total minutes since midnight
    seconds_since_midnight = (dt.hour * 60 + dt.minute) * 60 + dt.second

    # Find the next multiple of the interval
    next_interval_second = ((seconds_since_midnight // interval_seconds) + 1) * interval_seconds

    # Calculate the time of the next interval
    next_interval_time = datetime(dt.year, dt.month, dt.day, 0, 0) + timedelta(seconds=next_interval_second)

    # Calculate the number of seconds until the next interval
    seconds_to_next = (next_interval_time - dt).total_seconds()

    return seconds_to_next


def are_in_same_bar(interval_seconds: int, time_ms1: int, time_ms2: int) -> bool:
    a = int(time_ms1 / 1000 / interval_seconds)
    b = int(time_ms2 / 1000 / interval_seconds)
    return a == b


def get_bar_time_ms(interval_ms: int, time_ms_ref: int) -> int:
    return int(time_ms_ref / interval_ms) * interval_ms


def is_midnight() -> bool:
    # Get the current local time
    now = datetime.now()

    # Get the hour component of the current time
    hour = now.hour

    return hour < 7

def get_monthly_third_friday(year, month):
    # 获取当月第一天
    first_day = date(year, month, 1)
    # 获取当月第一个星期五
    first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
    # 获取当月第三个星期五
    third_friday = first_friday + timedelta(weeks=2)
    return third_friday
    
if __name__ == '__main__':
    print(get_monthly_third_friday(2025, 9).strftime("%Y%m%d"))
