import requests
import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from datetime import datetime, timedelta
# import matplotlib.pyplot as plt

try:
    import config
except ImportError:
    import APIs.config as config
# https://www.investopedia.com/articles/active-trading/101014/basics-algorithmic-trading-concepts-and-examples.asp

# Golden Cross strategy - based on 15 and 5 period moving average
# RSI strategy - price below 30? Go long. Above 70? Go short.

api_key_oanda = config.oanda_key
accountID_oanda = config.oanda_account
url_oanda = "https://api-fxpractice.oanda.com"

client_oanda = API(access_token=api_key_oanda)

api_key_av = config.av_key
url_av = "https://www.alphavantage.co/query?"


def live_algo_chart(ccy_1, ccy_2, strategy):
    """Requests technical indicator and price data and returns a dataframe.

    Parameters:
    ccy1 (str): The first currency.
    ccy2 (str): The second currency.
    strategy (str): The strategy determines the indicators that will be added
                    to the charts.
                    Golden Cross - SMA and EMA
                    RSI - RSI

    Returns:
    dataframe: a dataframe that can be plotted in the GUI.
    """

    currency_pair = ccy_1 + ccy_2
    dfunction = "chart"
    strategy_indicator = {"Golden Cross": "SMA", "RSI": "RSI"}
    indicator = strategy_indicator.get(strategy)

    fx_dataframe_ascending = Algo_fx_data(ccy_1, ccy_2, dfunction)

    if strategy == "Golden Cross":
        sma_short_term = Algo_technical_indicators(indicator, currency_pair, dfunction)
        sma_long_term = Algo_technical_indicators(indicator, currency_pair, dfunction, 15)
        merged_dataframes = fx_dataframe_ascending.merge(sma_short_term, on="Date").merge(sma_long_term, on="Date")
        return merged_dataframes

    elif strategy == "RSI":
        rsi_short_term = Algo_technical_indicators(indicator, currency_pair, dfunction)
        merged_dataframes = fx_dataframe_ascending.merge(rsi_short_term, on="Date")
        return merged_dataframes

    else:
        pass


def Algo_fx_data(ccy_1, ccy_2, dfunction):
    """Requestsprice data and returns a dataframe.

    Parameters:
    ccy1 (str): The first currency.
    ccy2 (str): The second currency.
    dfunction (str): Determines whether the dataframe is used to
                     create a chart(chart) or show prices(algo)

    Returns:
    dataframe: a dataframe that can be merged with another dataframe.
    """

    function = "FX_INTRADAY"
    interval = "1min"
    time_series = "Time Series FX (1min)"

    parameters = {"function": function, "from_symbol": ccy_1,
                  "to_symbol": ccy_2, "apikey": api_key_av,
                  "interval": interval}
    response = requests.get(url_av, params=parameters)
    fx_rate_json = response.json()

    fx_rate = fx_rate_json[time_series]

    fx_rate_extract = []
    for dates, prices in fx_rate.items():
        fx_rate_extract.append({"Date": dates,
                                "Close Price": float(prices["4. close"])})

    fx_dataframe = pd.DataFrame(fx_rate_extract)
    fx_dataframe_ascending = fx_dataframe[::-1]  # json default is descending.

    if dfunction == "chart":
        return fx_dataframe_ascending

    elif dfunction == "algo":
        return fx_dataframe_ascending.tail(1)

    else:
        pass


def Algo_technical_indicators(indicator, currency_pair, dfunction, period=5):
    """Requests technical indicator data and returns a dataframe.

    Parameters:
    currency_pair: The currencies in an alpha vantage format
    dfunction (str): Determines whether the dataframe is used to create a chart
                     or show prices
    period (int): Default value is 5. The number of periods the Technical
                  indicator is calculated with.
    Returns:
    dataframe: a dataframe that can be merged with another dataframe.
    """

    interval = "1min"

    parameters = {"function": indicator,
                  "symbol": currency_pair, "interval": interval,
                  "time_period": period, "series_type": "close",
                  "apikey": api_key_av}

    response = requests.get(url_av, params=parameters)
    ti_json = response.json()

    ti_meta = ti_json["Technical Analysis: {}".format(indicator)]

    ti_extract = []
    for dates, values in ti_meta.items():
        ti_extract.append({"Date": dates, "Value": float(values[indicator])})

    ti_dataframe = pd.DataFrame(ti_extract)

    # I need to add ":00" to all intaday dates to merge with the fx_dataframe.
    # technical indicators use EST, fx prices use UTC. Hence the conversion.

    ti_dataframe["Date"] = [est_to_utc(date+":00") for date in ti_dataframe["Date"]]

    ti_dataframe = ti_dataframe.rename(columns={"Value": "{}-day {} value".format(period, indicator)})
    ti_dataframe_ascending = ti_dataframe[::-1]  # data from json is in descending order
    if dfunction == "chart":
        return ti_dataframe_ascending

    elif dfunction == "algo":
        return ti_dataframe_ascending.tail(3)

    else:
        pass


def algo_execution(units, ccy1, ccy2, strategy):
    """Tracks the prices of a currency pair and returns the order fil or
    current price information if the algorithm strategy dictates that a
    trade should be executed

    Parameters:
    units (int): The quantity of Instrument units that will be Bought or Sold.

    ccy1 (str): The first currency.
    ccy2 (str): The second currency.
    strategy (str): The strategy determines the indicators that will be added
                    to the charts.
                    Golden Cross - SMA and EMA
                    RSI - RSI

    Returns:
    str: a string of the fil details or price information
    """

    units = abs(float(units))
    strategy_indicator = {"Golden Cross": "SMA", "RSI": "RSI"}
    indicator = strategy_indicator.get(strategy)
    current_price = Algo_fx_data(ccy1, ccy2, "algo").at[0, "Close Price"]
    currency_pair = ccy1 + ccy2
    oanda_instrument = "{}_{}".format(ccy1, ccy2)

    if indicator == "SMA":

        sma_long_prior = Algo_technical_indicators(indicator, currency_pair, "algo", 15).at[2, "15-day {} value".format(indicator)]
        sma_short_prior = Algo_technical_indicators(indicator, currency_pair, "algo").at[2, "5-day {} value".format(indicator)]
        direction_prior = float(sma_short_prior) - float(sma_long_prior)

        sma_short_current = Algo_technical_indicators(indicator, currency_pair, "algo").at[0, "5-day {} value".format(indicator)]
        sma_long_current = Algo_technical_indicators(indicator, currency_pair, "algo", 15).at[0, "15-day {} value".format(indicator)]
        direction_current = float(sma_short_current) - float(sma_long_current)

        if direction_current > 0 and direction_prior < 0:
            execution = algo_market_order(units, oanda_instrument)
            return "Buy Order Sent\n {}".format(algo_execution_details(execution))

        elif direction_current < 0 and direction_prior > 0:
            units = units * -1
            execution = algo_market_order(units, oanda_instrument)
            return "Sell Order Sent\n {}".format(algo_execution_details(execution))

        else:
            return " Current Price: {}\n 5-day SMA {}\n 15-day SMA {}".format(current_price,
            sma_short_current, sma_long_current)

    elif indicator == "RSI":
        rsi_short_term = Algo_technical_indicators(indicator, currency_pair, "algo").at[0, "5-day {} value".format(indicator)]

        if rsi_short_term <= 30:
            execution = algo_market_order(units, oanda_instrument)
            return "Buy Order Sent\n {}".format(algo_execution_details(execution))

        elif rsi_short_term >= 70:
            units = units * - 1
            execution = algo_market_order(units, oanda_instrument)
            return "Sell Order Sent\n {}".format(algo_execution_details(execution))

        else:
            return " Current Price: {}\n 5-day RSI {}".format(current_price,
            rsi_short_term)

    else:
        return "API error"


def est_to_utc(time):
    """Converts the EST time for intraday data into UTC time"""
    est_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    utc = est_time + timedelta(hours=4)
    return str(utc)


def algo_market_order(units, oanda_instrument):
    # data must be organised as a JSON orderbody data (JSON (required)) – json orderbody to send
    """Send a trade order to Oanda and return a JSON response of the trade
    confirmation

    Parameters:
    units (int): The quantity of Instrument units that will be Bought or Sold.

    instrument (str): The Instrument that will be traded.

    Returns:
    JSON: a JSON value that can be converted into a string.
    """

    params_data = {"units": units, "instrument": oanda_instrument}
    datax = {
"order": {
"units": units,
"instrument": oanda_instrument,
"timeInForce": "FOK",
"type": "MARKET",
"positionFill": "DEFAULT"
}
}
    order = orders.OrderCreate(accountID=accountID_oanda, data=datax)
    client_oanda.request(order)

    order_details = order.response
    return order_details


def algo_execution_details(order_details):
    """Converts a JSON trade confirmation into a readable string

    Parameters:
    order details (json): The JSON response from oanda.

    Returns:
    str: The trade confirmation in string format.
    """

    fil = order_details

    fil_type = fil["orderFillTransaction"]["type"]
    fil_execution_time = fil["orderFillTransaction"]["time"].replace("T", " ")

    fil_instrument = fil["orderFillTransaction"]["instrument"]
    fil_units = fil["orderFillTransaction"]["units"]
    fil_price = fil["orderFillTransaction"]["price"]
    fil_profit = fil["orderFillTransaction"]["pl"]

    fil_information = " {}\n Execution Time: {}\n\n Instrument: {}\n Units: {}\n Price: {}\n Gain/Loss: {}".format(fil_type, fil_execution_time,
    fil_instrument, fil_units, fil_price, fil_profit)

    return fil_information
