from sqlalchemy import create_engine, text
from datetime import timedelta, date, datetime
import pandas as pd


class ChinaMarketCalendar:
    def __init__(self, config, start_date, end_date):
        self.config = config
        self.db_config_name = "MarketDataRO"

        # Create SQLAlchemy engine with auth_plugin specification
        connection_string = self.config.get_mysql_string(self.db_config_name)
        self.engine = create_engine(connection_string)

        self.start_date = start_date
        self.end_date = end_date

        self.calendar = self.get_calendar(start_date, end_date)
        # print(self.calendar.dtypes)

    def get_calendar(self, start_date, end_date):
        sql = text("SELECT * FROM Calendar WHERE date >= :start AND date <= :end ORDER BY date")
        calendar = pd.read_sql(sql, self.engine, params={
            'start': start_date,
            'end': end_date
        })
        return calendar

    def get_pre_trading_day(self, d):
        pre_trading = d + timedelta(days=-1)
        while self.calendar[(self.calendar.date == pre_trading) & (self.calendar.isOpen == 1)].empty:
            # print("%s is not trading day. go back one day." % pre_trading)
            pre_trading = pre_trading + timedelta(days=-1)
        return pre_trading

    def get_next_trading_day(self, d):
        next_trading = d + timedelta(days=1)
        while self.calendar[(self.calendar.date == next_trading) & (self.calendar.isOpen == 1)].empty:
            # print("%s is not trading day. go further one day." % next_trading)
            next_trading = next_trading + timedelta(days=1)
        return next_trading

    def get_date_on_which_has_days_to_trade(self, last_date, days_to_trade):
        t = self.calendar[(self.calendar.date <= last_date) & (self.calendar.isOpen == True)]
        if t.shape[0] < days_to_trade:
            return t.iloc[0].date
        return t.iloc[-days_to_trade].date

    def get_days_to_live(self, day):
        t = self.calendar[
            (self.calendar.date >= date.today()) & (self.calendar.date <= day) & (self.calendar.isOpen == True)]
        return t.shape[0]

    def is_trading_day(self, day):
        df = self.calendar[(self.calendar.date == day) & (self.calendar.isOpen == 1)]
        return not df.empty
