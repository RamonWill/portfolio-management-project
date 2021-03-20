import requests
import pandas as pd
from datetime import datetime, timedelta
from external_connections.ConnectionObject import ConnectionObject


class AlphaVantageAPI(object):
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.connection_status = False
        self.BASE_URL = "https://www.alphavantage.co/query?"
        self._get_status()

    def _get_status(self):
        params = {"apikey": self.api_key, "function": "OVERVIEW", "symbol": "CAT"}
        response = requests.get(self.BASE_URL, params=params)
        test_response = response.json()
        self.connection_status = "Symbol" in test_response

    def get_fx_prices(self, intervals, from_symbol, to_symbol):
        if not self.connection_status:
            return []
        fx_series = {
            "INTRADAY": "Time Series FX (5min)",
            "DAILY": "Time Series FX (Daily)",
            "WEEKLY": "Time Series FX (Weekly)",
        }
        periods = f"FX_{intervals}"
        fx_series_name = fx_series[intervals]

        params = {
            "apikey": self.api_key,
            "function": periods,
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
        }
        if intervals == "INTRADAY":
            params["interval"] = "5min"

        response = requests.get(self.BASE_URL, params)
        all_fx_prices = response.json()
        all_fx_prices_dict = all_fx_prices[fx_series_name]
        all_close_prices = []
        for date in all_fx_prices_dict:
            close_price = all_fx_prices_dict[date]["4. close"]
            fx_price = FXPriceData(date, close_price)
            all_close_prices.append(fx_price)
        all_close_prices.sort(key=lambda x: x.date)
        return all_close_prices

    def get_fx_prices_with_techincal(
        self, intervals, from_symbol, to_symbol, technical_indicator
    ):
        currency_pair = f"{from_symbol}{to_symbol}"
        fx_series = {"INTRADAY": "5min", "DAILY": "daily", "WEEKLY": "weekly"}
        fx_series_interval = fx_series[intervals]
        params = {
            "function": technical_indicator,
            "symbol": currency_pair,
            "interval": fx_series_interval,
            "time_period": 5,
            "series_type": "close",
            "time_period": 5,
            "series_type": "close",
            "apikey": self.api_key,
        }
        response = requests.get(self.BASE_URL, params)
        all_indicator_data = response.json()
        fx_indicator_name = f"Technical Analysis: {technical_indicator}"
        all_indicator_data_dict = all_indicator_data[fx_indicator_name]
        results = []
        for date in all_indicator_data_dict:
            value = all_indicator_data_dict[date][technical_indicator]
            data = FXIndicatorData(date, technical_indicator, value)
            results.append(data)
        return results


class FXPriceData(ConnectionObject):
    def __init__(self, date, close_price):
        self.date = date
        self.close_price = float(close_price)

    def __repr__(self):
        return f"{self.date}: {self.close_price}"


class FXIndicatorData(ConnectionObject):
    def __init__(self, date, indicator, value):
        self.date = date
        self.value = float(value)
        self.indicator = indicator

    def __repr__(self):
        return f"{self.date} {self.indicator}: {self.close_price}"
