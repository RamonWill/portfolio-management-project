import requests
import pandas as pd
from oandapyV20 import API


try:
    from config import Configurations
except ImportError:
    from models.config import Configurations
    from models.oanda_api import market_order, execution_details
    from models.vantage_alpha_api import est_to_utc
# https://www.investopedia.com/articles/active-trading/101014/basics-algorithmic-trading-concepts-and-examples.asp

# Golden Cross strategy - based on 15 and 5 period moving average
# RSI strategy - price below 30? Go long. Above 70? Go short.

api_key_oanda = Configurations.OANDA_KEY
accountID_oanda = Configurations.OANDA_ACCOUNT
url_oanda = "https://api-fxpractice.oanda.com"

client_oanda = API(access_token=api_key_oanda)

api_key_av = Configurations.AV_KEY
url_av = "https://www.alphavantage.co/query?"


class Algo(object):
    """The Algo object is used to create charts or initiate trade executions
       based on particular strategies.

    Args:
        ccy1 (str): The first currency.
        ccy2 (str): The second currency.
        current_pair: The currencies in an alpha vantage format.
    """

    def __init__(self, ccy_1, ccy_2):
        self.ccy_1 = ccy_1
        self.ccy_2 = ccy_2
        self.currency_pair = ccy_1 + ccy_2

    def live_algo_chart(self, strategy="Golden Cross"):
        """Requests technical indicator and price data and returns a dataframe.

        Parameters:
        strategy (str): The strategy determines the indicators that will be
                        added to the charts.
                        Golden Cross - SMA
                        RSI - RSI

        Returns:
        dataframe: a dataframe that can be plotted in the GUI.
        """

        dfunction = "chart"
        strategy_indicator = {"Golden Cross": "SMA", "RSI": "RSI"}
        indicator = strategy_indicator.get(strategy)

        fx_data = self.Algo_fx_data(dfunction)

        if strategy == "Golden Cross":
            sma_short_term = self.Algo_ti(indicator, dfunction)
            sma_long_term = self.Algo_ti(indicator, dfunction, 15)
            df_merged = fx_data.merge(sma_short_term, on="Date").merge(sma_long_term, on="Date")
            df_merged = df_merged.rename(columns={"SMA_x": "5-period SMA value", "SMA_y": "15-period SMA value"})
            return df_merged

        elif strategy == "RSI":
            rsi_short_term = self.Algo_ti(indicator, dfunction)
            df_merged = fx_data.merge(rsi_short_term, on="Date")
            df_merged = df_merged.rename(columns={"RSI": "5-period RSI value"})
            return df_merged

        else:
            pass

    def Algo_fx_data(self, dfunction="chart"):
        """Requestsprice data and returns a dataframe.

        Parameters:
        dfunction (str): Determines whether the dataframe is used to
                         create a chart(chart) or show prices(algo)

        Returns:
        dataframe: a dataframe that can be merged with another dataframe.
        """

        function = "FX_INTRADAY"
        interval = "1min"
        time_series = "Time Series FX (1min)"

        parameters = {"function": function, "from_symbol": self.ccy_1,
                      "to_symbol": self.ccy_2, "apikey": api_key_av,
                      "interval": interval}
        response = requests.get(url_av, params=parameters)
        fx_rate_json = response.json()

        fx_rate = fx_rate_json[time_series]

        fx_rate_extract = pd.DataFrame.from_dict(fx_rate, orient="index", columns = ["4. close"]).reset_index()
        fx_rate_extract = fx_rate_extract.rename(columns={"index": "Date", "4. close": "Close Price"})
        fx_rate_extract["Close Price"] = pd.to_numeric(fx_rate_extract["Close Price"])

        if dfunction == "chart":
            return fx_rate_extract

        elif dfunction == "algo":
            return fx_rate_extract.tail(1)

        else:
            pass

    def Algo_ti(self, indicator, dfunction="chart", period=5):
        """Requests technical indicator data and returns a dataframe.

        Parameters:
        indicator: Either SMA or RSI
        dfunction (str): Determines whether the dataframe is used to create a
                         chart or show prices
        period (int): Default value is 5. The number of periods the Technical
                      indicator is calculated with.
        Returns:
        dataframe: a dataframe that can be merged with another dataframe.
        """

        interval = "1min"

        parameters = {"function": indicator,
                      "symbol": self.currency_pair, "interval": interval,
                      "time_period": period, "series_type": "close",
                      "apikey": api_key_av}

        response = requests.get(url_av, params=parameters)
        ti_json = response.json()

        ti_meta = ti_json["Technical Analysis: {}".format(indicator)]
        ti_dataframe = pd.DataFrame.from_dict(ti_meta, orient="index").reset_index()
        ti_dataframe[indicator] = pd.to_numeric(ti_dataframe[indicator])
        ti_dataframe = ti_dataframe.rename(columns={"Value": "{}-period {} value".format(period, indicator),
                                                    "index": "Date"})

        # I add ":00" to all intaday dates to merge it with the fx_dataframe.
        # technical indicators = EST, fx prices = UTC. Hence the conversion.

        ti_dataframe["Date"] = [est_to_utc(date+":00") for date in ti_dataframe["Date"]]

        if dfunction == "chart":
            return ti_dataframe

        elif dfunction == "algo":
            return ti_dataframe.tail(3)

        else:
            pass

    def algo_execution(self, units, strategy):
        """Tracks the prices of a currency pair and returns the order fil or
        current price information if the algorithm strategy dictates that a
        trade should be executed

        Parameters:
        units (int): The Instrument units that will be Bought or Sold.

        strategy (str): The strategy determines the indicators that will be
                        added to the charts.
                        Golden Cross - SMA and EMA
                        RSI - RSI

        Returns:
        str: a string of the fil details or price information
        """

        units = abs(float(units))
        strategy_indicator = {"Golden Cross": "SMA", "RSI": "RSI"}
        indicator = strategy_indicator.get(strategy)
        oanda_instrument = "{}/{}".format(self.ccy_1, self.ccy_2)

        if indicator == "SMA":
            df_sma_short = self.Algo_ti(indicator, "algo").reset_index(drop=True)
            df_sma_long = self.Algo_ti(indicator, "algo", 15).reset_index(drop=True)

            sma_long_prior = df_sma_long.at[2, "{}".format(indicator)]
            sma_short_prior = df_sma_short.at[2, "{}".format(indicator)]
            direction_prior = float(sma_short_prior) - float(sma_long_prior)

            sma_long_current = df_sma_long.at[0, "{}".format(indicator)]
            sma_short_current = df_sma_short.at[0, "{}".format(indicator)]
            direction_current = float(sma_short_current) - float(sma_long_current)

            if direction_current > 0 and direction_prior < 0:  # Golden Cross
                execution = market_order(units, oanda_instrument)
                return "Buy Order Sent\n {}".format(execution_details(execution))

            elif direction_current < 0 and direction_prior > 0:  # Death Cross
                units = units * -1
                execution = market_order(units, oanda_instrument)
                return "Sell Order Sent\n {}".format(execution_details(execution))

            else:
                current_price = self.Algo_fx_data("algo").reset_index(drop=True)
                current_price = current_price.at[0, "Close Price"]
                return "Current Price: {}\n 5-period SMA {}\n 15-period SMA {}".format(current_price,
                sma_short_current, sma_long_current)

        elif indicator == "RSI":
            rsi_short_term = self.Algo_ti(indicator, "algo").reset_index(drop=True)
            rsi_short_term = rsi_short_term.at[0, "{}".format(indicator)]

            if rsi_short_term <= 30:
                execution = market_order(units, oanda_instrument)
                return "Buy Order Sent\n {}".format(execution_details(execution))

            elif rsi_short_term >= 70:
                units = units * - 1
                execution = market_order(units, oanda_instrument)
                return "Sell Order Sent\n {}".format(execution_details(execution))

            else:
                current_price = self.Algo_fx_data("algo").at[0, "Close Price"]
                return " Current Price: {}\n 5-period RSI {}".format(current_price,
                rsi_short_term)

        else:
            return "API error"
