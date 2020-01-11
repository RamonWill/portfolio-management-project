import requests
import pandas as pd
from datetime import datetime, timedelta


try:
    import config
except ImportError:
    import APIs.config as config

api_key = config.av_key
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

    def Fx_chart_gui(self):
        """Requests technical indicator AND price data and returns
           a dataframe that can be plotted in the GUI.
        """

        ti_list = {"RSI", "SMA", "EMA"}
        self.date_range = self.date_range.upper()

        if self.indicator == "No Indicator":
            fx_dataframe = self.Alpha_fx_data()
            return fx_dataframe

        elif self.indicator.upper() in ti_list:
            fx_dataframe = self.Alpha_fx_data()
            ti_dataframe = self.Technical_indicators()
            merged_dataframes = fx_dataframe.merge(ti_dataframe, on="Date")
            return merged_dataframes

        else:
            pass

    def Alpha_fx_data(self):
        """Requests price data and returns a dataframe."""

        if self.date_range == "INTRADAY":
            function = "FX_INTRADAY"
            interval = "5min"
            time_series = "Time Series FX (5min)"
            parameters = {"function": function,
                          "from_symbol": self.ccy_1,
                          "to_symbol": self.ccy_2,
                          "apikey": api_key,
                          "interval": interval}

        elif self.date_range == "DAILY":
            function = "FX_DAILY"
            interval = "daily"
            time_series = "Time Series FX (Daily)"
            parameters = {"function": function,
                          "from_symbol": self.ccy_1,
                          "to_symbol": self.ccy_2,
                          "apikey": api_key}

        elif self.date_range == "WEEKLY":
            function = "FX_WEEKLY"
            interval = "weekly"
            time_series = "Time Series FX (Weekly)"
            parameters = {"function": function,
                          "from_symbol": self.ccy_1,
                          "to_symbol": self.ccy_2,
                          "apikey": api_key}
        else:
            pass

        response = requests.get(url, params=parameters)
        fx_rate_json = response.json()

        fx_rate = fx_rate_json[time_series]

        fx_rate_extract = pd.DataFrame.from_dict(fx_rate,
                                                 orient="index",
                                                 columns=["4. close"]).reset_index()

        fx_rate_extract = fx_rate_extract.rename(columns={"index": "Date",
                                                          "4. close": "Close Price"})

        fx_rate_extract["Close Price"] = pd.to_numeric(fx_rate_extract["Close Price"])

        return fx_rate_extract

    def Technical_indicators(self):
        """Requests technical indicator data and returns a dataframe."""
        if self.date_range == "INTRADAY":
            interval = "5min"

        elif self.date_range == "DAILY":
            interval = "daily"

        elif self.date_range == "WEEKLY":
            interval = "weekly"

        else:
            pass

        parameters = {"function": self.indicator,
                      "symbol": self.currency_pair, "interval": interval,
                      "time_period": 5, "series_type": "close",
                      "apikey": api_key}

        response = requests.get(url, params=parameters)
        ti_json = response.json()

        ti_meta = ti_json["Technical Analysis: {}".format(self.indicator)]

        ti_dataframe = pd.DataFrame.from_dict(ti_meta,
                                              orient="index").reset_index()

        ti_dataframe[self.indicator] = pd.to_numeric(ti_dataframe[self.indicator])
        ti_dataframe = ti_dataframe.rename(columns={self.indicator: "5-period {} value".format(self.indicator),
                                                    "index": "Date"})
        #  ":00" is added to all intraday dates to merge with the fx_dataframe
        if interval == "5min":
            ti_dataframe["Date"] = [est_to_utc(date+":00")
                                    for date in ti_dataframe["Date"]]

        return ti_dataframe


def est_to_utc(time):
    """Converts the EST time for intraday data into UTC time"""

    est_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    utc = est_time + timedelta(hours=5)
    return str(utc)
