import requests
import pandas as pd
from datetime import datetime, timedelta
# import matplotlib.pyplot as plt

try:
    import config
except ImportError:
    import APIs.config as config

api_key = config.av_key
url = "https://www.alphavantage.co/query?"


def Fx_chart_gui(date_range, ccy_1, ccy_2, indicator):
    """Requests technical indicator AND price data and returns a dataframe.

    Parameters:
    date range (str): The axis period for the chart.
    ccy1 (str): The first currency.
    ccy2 (str): The second currency.
    indicator (str): The Technical Indicator to add to a chart.

    Returns:
    dataframe: a dataframe that can be plotted in the GUI.
    """
    currency_pair = ccy_1 + ccy_2
    ti_list = {"RSI", "SMA", "EMA"}
    date_range = date_range.upper()

    if indicator == "No Indicator":
        fx_dataframe_ascending = Alpha_fx_data(date_range, ccy_1, ccy_2)
        return fx_dataframe_ascending

    elif indicator.upper() in ti_list:
        fx_dataframe_ascending = Alpha_fx_data(date_range, ccy_1, ccy_2)
        ti_dataframe_ascending = Technical_indicators(indicator, currency_pair, date_range)
        merged_dataframes = fx_dataframe_ascending.merge(ti_dataframe_ascending, on="Date")
        return merged_dataframes

    else:
        pass


def Alpha_fx_data(date_range, ccy_1, ccy_2):
    """Requests price data and returns a dataframe."""

    if date_range == "INTRADAY":
        function = "FX_INTRADAY"
        interval = "5min"
        time_series = "Time Series FX (5min)"
        parameters = {"function": function, "from_symbol": ccy_1,
                      "to_symbol": ccy_2,
                      "apikey": api_key,
                      "interval": interval}

    elif date_range == "DAILY":
        function = "FX_DAILY"
        interval = "daily"
        time_series = "Time Series FX (Daily)"
        parameters = {"function": function,
                      "from_symbol": ccy_1,
                      "to_symbol": ccy_2,
                      "apikey": api_key}

    elif date_range == "WEEKLY":
        function = "FX_WEEKLY"
        interval = "weekly"
        time_series = "Time Series FX (Weekly)"
        parameters = {"function": function,
                      "from_symbol": ccy_1,
                      "to_symbol": ccy_2,
                      "apikey": api_key}
    else:
        pass

    response = requests.get(url, params=parameters)
    fx_rate_json = response.json()

    fx_rate = fx_rate_json[time_series]

    fx_rate_extract = []
    for dates, prices in fx_rate.items():
        fx_rate_extract.append({"Date": dates, "Close Price": float(prices["4. close"])})

    fx_dataframe = pd.DataFrame(fx_rate_extract)
    fx_dataframe_ascending = fx_dataframe[::-1]  # json data descends

    return fx_dataframe_ascending


def Technical_indicators(indicator, currency_pair, date_range):
    """Requests technical indicator data and returns a dataframe."""
    if date_range == "INTRADAY":
        interval = "5min"

    elif date_range == "DAILY":
        interval = "daily"

    elif date_range == "WEEKLY":
        interval = "weekly"

    else:
        pass

    parameters = {"function": indicator,
                  "symbol": currency_pair, "interval": interval,
                  "time_period": 5, "series_type": "close",
                  "apikey": api_key}

    response = requests.get(url, params=parameters)
    ti_json = response.json()

    ti_meta = ti_json["Technical Analysis: {}".format(indicator)]

    ti_extract = []
    for dates, values in ti_meta.items():
        ti_extract.append({"Date": dates, "Value": float(values[indicator])})

    ti_dataframe = pd.DataFrame(ti_extract)

    #  ":00" is added to all intraday dates to merge with the fx_dataframe
    if interval == "5min":
        ti_dataframe["Date"] = [est_to_utc(date+":00") for date in ti_dataframe["Date"]]

    ti_dataframe = ti_dataframe.rename(columns={"Value": "{} value".format(indicator)})
    ti_dataframe_ascending = ti_dataframe[::-1]  # json data descends

    return ti_dataframe_ascending


def est_to_utc(time):
    """Converts the EST time for intraday data into UTC time"""

    est_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    utc = est_time + timedelta(hours=4)
    return str(utc)
