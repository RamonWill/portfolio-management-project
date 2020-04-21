import requests
import pandas as pd
from datetime import datetime, timedelta


try:
    from config import Configurations
except ImportError:
    from Models.config import Configurations

api_key = Configurations.AV_KEY
url = "https://www.alphavantage.co/query?"


class AV_FXData(object):
    """The AV_FXData object is used to create charts or initiate
       trade executions based on particular strategies.

    Args:
        date range (str): The axis period for the chart.
        ccy1 (str): The first currency.
        ccy2 (str): The second currency.
        indicator (str): The Technical Indicator to add to a chart.
    """

    def __init__(self, date_range, ccy_1, ccy_2, indicator="No Indicator"):

        self.date_range = date_range
        self.ccy_1 = ccy_1
        self.ccy_2 = ccy_2
        self.indicator = indicator
        self.currency_pair = ccy_1 + ccy_2

    def fx_chart_gui(self):
        """Requests technical indicator AND price data and returns
           a dataframe that can be plotted in the GUI.
        """

        ti_list = {"RSI", "SMA", "EMA"}
        self.date_range = self.date_range.upper()

        if self.indicator == "No Indicator":
            fx_dataframe = self.alpha_fx_data()
            return fx_dataframe

        elif self.indicator.upper() in ti_list:
            fx_dataframe = self.alpha_fx_data()
            ti_dataframe = self.technical_indicators()
            merged_dataframes = fx_dataframe.merge(ti_dataframe, on="Date")
            return merged_dataframes
        else:
            raise ValueError("The chosen indicator is not valid")

    def alpha_fx_data(self):
        """Requests price data and returns a dataframe."""
        date_series = {"INTRADAY": "Time Series FX (5min)",
                       "DAILY": "Time Series FX (Daily)",
                       "WEEKLY": "Time Series FX (Weekly)"}

        function = f"FX_{self.date_range}"
        time_series = date_series[self.date_range]

        parameters = {"function": function,
                      "from_symbol": self.ccy_1,
                      "to_symbol": self.ccy_2,
                      "apikey": api_key}

        if self.date_range == "INTRADAY":
            parameters["interval"] = "5min"

        response = requests.get(url, params=parameters)
        fx_rate_json = response.json()
        fx_rate = fx_rate_json[time_series]  # raise error if this fails

        fx_extract = pd.DataFrame.from_dict(fx_rate,
                                            orient="index",
                                            columns=["4. close"]).reset_index()
        renamed_headers = {"index": "Date", "4. close": "Close Price"}
        fx_extract = fx_extract.rename(columns=renamed_headers)

        fx_extract["Close Price"] = pd.to_numeric(fx_extract["Close Price"])

        return fx_extract

    def technical_indicators(self):
        """Requests technical indicator data and returns a dataframe."""
        intervals = {"INTRADAY": "5min",
                     "DAILY": "daily",
                     "WEEKLY": "weekly"}

        interval = intervals[self.date_range]
        parameters = {"function": self.indicator,
                      "symbol": self.currency_pair, "interval": interval,
                      "time_period": 5, "series_type": "close",
                      "time_period": 5, "series_type": "close",
                      "apikey": api_key}

        response = requests.get(url, params=parameters)
        ti_json = response.json()
        ti_meta = ti_json[f"Technical Analysis: {self.indicator}"]

        ti_dataframe = pd.DataFrame.from_dict(ti_meta,
                                              orient="index").reset_index()

        ti_dataframe[self.indicator] = pd.to_numeric(ti_dataframe[self.indicator])

        period = f"5-period {self.indicator} value"
        renamed_headers = {self.indicator: period, "index": "Date"}
        ti_dataframe = ti_dataframe.rename(columns=renamed_headers)

        if interval == "5min":
            new_dates = [est_to_utc(d+":00") for d in ti_dataframe["Date"]]
            ti_dataframe["Date"] = new_dates

        return ti_dataframe


def est_to_utc(time):
    """Converts the EST time for intraday data into UTC time"""

    est_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    utc = est_time + timedelta(hours=5)
    return str(utc)
