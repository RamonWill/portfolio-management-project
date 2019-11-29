import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
# import requests

# documentation - https://oanda-api-v20.readthedocs.io/en/latest/
# the import error exception is raised if i run this file from prmsystem_api

try:
    import config
except ImportError:
    import APIs.config as config


api_key = config.oanda_key
accountID = config.oanda_account
url = "https://api-fxpractice.oanda.com"

client = API(access_token=api_key)

instrument_names = {'USD_ZAR': 'USD/ZAR', 'NATGAS_USD': 'Natural Gas', 'USB05Y_USD': 'US 5Y T-Note', 'GBP_HKD': 'GBP/HKD', 'US30_USD': 'US Wall St 30',
'SUGAR_USD': 'Sugar', 'XPD_USD': 'Palladium', 'US2000_USD': 'US Russ 2000', 'EUR_GBP': 'EUR/GBP', 'XAU_HKD': 'Gold/HKD', 'GBP_SGD': 'GBP/SGD',
'USD_SEK': 'USD/SEK', 'EUR_CAD': 'EUR/CAD', 'HK33_HKD': 'Hong Kong 33', 'USD_TRY': 'USD/TRY', 'GBP_JPY': 'GBP/JPY', 'GBP_PLN': 'GBP/PLN', 'WHEAT_USD': 'Wheat',
'EUR_JPY': 'EUR/JPY', 'TWIX_USD': 'Taiwan Index', 'XAU_JPY': 'Gold/JPY', 'EUR_HKD': 'EUR/HKD', 'USB02Y_USD': 'US 2Y T-Note', 'XAU_AUD': 'Gold/AUD',
'IN50_USD': 'India 50', 'USD_CNH': 'USD/CNH', 'XAU_CAD': 'Gold/CAD', 'NZD_USD': 'NZD/USD', 'XAG_AUD': 'Silver/AUD', 'XAG_HKD': 'Silver/HKD', 'EUR_HUF':
'EUR/HUF', 'JP225_USD': 'Japan 225', 'SGD_HKD': 'SGD/HKD', 'AUD_NZD': 'AUD/NZD', 'SPX500_USD': 'US SPX 500', 'EUR_USD': 'EUR/USD', 'USD_PLN': 'USD/PLN',
'GBP_AUD': 'GBP/AUD', 'USD_CZK': 'USD/CZK', 'EUR_TRY': 'EUR/TRY', 'USD_JPY': 'USD/JPY', 'EUR_SEK': 'EUR/SEK', 'USD_SGD': 'USD/SGD', 'EUR_SGD': 'EUR/SGD',
'CHF_JPY': 'CHF/JPY', 'USD_DKK': 'USD/DKK', 'XAU_GBP': 'Gold/GBP', 'XAG_USD': 'Silver', 'UK10YB_GBP': 'UK 10Y Gilt', 'XAG_JPY': 'Silver/JPY', 'EUR_AUD': 'EUR/AUD',
'USD_HKD': 'USD/HKD', 'NZD_CAD': 'NZD/CAD', 'XAG_EUR': 'Silver/EUR', 'SOYBN_USD': 'Soybeans', 'GBP_ZAR': 'GBP/ZAR', 'NZD_SGD': 'NZD/SGD', 'ZAR_JPY': 'ZAR/JPY',
'USB10Y_USD': 'US 10Y T-Note', 'XAG_CHF': 'Silver/CHF', 'XPT_USD': 'Platinum', 'EU50_EUR': 'Europe 50', 'CAD_JPY': 'CAD/JPY', 'GBP_CAD': 'GBP/CAD', 'USD_SAR': 'USD/SAR', 'XAU_CHF': 'Gold/CHF', 'EUR_PLN': 'EUR/PLN', 'BCO_USD': 'Brent Crude Oil', 'NZD_HKD': 'NZD/HKD', 'NZD_CHF': 'NZD/CHF', 'XAG_GBP': 'Silver/GBP', 'UK100_GBP': 'UK 100', 'AUD_JPY': 'AUD/JPY', 'USD_CAD': 'USD/CAD', 'XCU_USD': 'Copper', 'DE30_EUR': 'Germany 30', 'NAS100_USD': 'US Nas 100', 'EUR_ZAR': 'EUR/ZAR', 'XAU_EUR': 'Gold/EUR', 'CAD_SGD': 'CAD/SGD', 'USD_NOK': 'USD/NOK', 'HKD_JPY': 'HKD/JPY', 'NZD_JPY': 'NZD/JPY', 'XAG_NZD': 'Silver/NZD', 'FR40_EUR': 'France 40', 'USD_HUF': 'USD/HUF',
'EUR_CZK': 'EUR/CZK', 'CHF_ZAR': 'CHF/ZAR', 'AUD_HKD': 'AUD/HKD', 'GBP_NZD': 'GBP/NZD', 'CN50_USD': 'China A50', 'XAG_SGD': 'Silver/SGD', 'XAU_SGD': 'Gold/SGD',
'USD_INR': 'USD/INR', 'CAD_HKD': 'CAD/HKD', 'SGD_CHF': 'SGD/CHF', 'CAD_CHF': 'CAD/CHF', 'AUD_SGD': 'AUD/SGD', 'EUR_NOK': 'EUR/NOK', 'SG30_SGD': 'Singapore 30',
'AU200_AUD': 'Australia 200', 'EUR_CHF': 'EUR/CHF', 'USB30Y_USD': 'US T-Bond', 'XAG_CAD': 'Silver/CAD', 'GBP_USD': 'GBP/USD', 'USD_MXN': 'USD/MXN', 'USD_CHF': 'USD/CHF', 'XAU_USD': 'Gold', 'AUD_CHF': 'AUD/CHF', 'EUR_DKK': 'EUR/DKK', 'CORN_USD': 'Corn', 'AUD_USD': 'AUD/USD', 'NL25_EUR': 'Netherlands 25', 'WTICO_USD': 'West Texas Oil', 'DE10YB_EUR': 'Bund', 'CHF_HKD': 'CHF/HKD', 'USD_THB': 'USD/THB', 'GBP_CHF': 'GBP/CHF', 'TRY_JPY': 'TRY/JPY', 'XAU_XAG': 'Gold/Silver', 'XAU_NZD': 'Gold/NZD', 'AUD_CAD': 'AUD/CAD', 'SGD_JPY': 'SGD/JPY', 'EUR_NZD': 'EUR/NZD'}


def Oanda_acc_summary():
    """Request the account details from oanda and return a dataframe."""
    account_details = accounts.AccountDetails(accountID)
    client.request(account_details)

    account_details = account_details.response

    dataframe_account = pd.DataFrame(account_details).loc[["NAV", "balance", "currency"]]
    dataframe_account = dataframe_account.drop(["lastTransactionID"], axis=1)

    dataframe_account.reset_index(inplace=True)

    return dataframe_account


def Oanda_prices():
    """Request instrument prices from oanda and return a dataframe."""
    instrument_keys = list(instrument_names)
    instrument_keys_sorted = sorted(instrument_keys)
    instrument_keys_sorted = ",".join(instrument_keys_sorted)

    params_prices = {"instruments": instrument_keys_sorted}
    pricing_details = pricing.PricingInfo(accountID=accountID, params=params_prices)
    client.request(pricing_details)

    pricing_details = pricing_details.response

    pricing_details = pricing_details["prices"]

    list_prices = []

    for header in pricing_details:
        instrument = header["instrument"]
        instrument_name = instrument_names.get(instrument)
        bid_price = header["bids"][0]["price"]
        ask_price = header["asks"][0]["price"]
        list_prices.append({"Instrument": instrument_name,
                            "Bid Price": bid_price,
                            "Ask Price": ask_price})

    dataframe_prices = pd.DataFrame(list_prices)

    dataframe_prices = dataframe_prices[["Instrument", "Bid Price", "Ask Price"]]

    return dataframe_prices


def Market_order(units, instrument, password):
    # data must be organised as a JSON orderbody data (JSON (required)) to send
    """Send a trade order to Oanda and return a JSON response of the trade
    confirmation

    Parameters:
    units (int): The quantity of Instrument units to Buy or Sell.
                     A positive integer is a Buy order whereas a negative
                     integer is a Sell order.
    instrument (str): The Instrument to Buy or Sell.
    password (str): The password that will allow the trade to be executed.

    Returns:
    JSON: a JSON value that can be converted into a string.
    """

    if password != "trade":
        return "wrong password"
    else:

        for keys, values in instrument_names.items():
            if instrument == values:
                oanda_instrument = keys

        datax = {
  "order": {
    "units": units,
    "instrument": oanda_instrument,
    "timeInForce": "FOK",
    "type": "MARKET",
    "positionFill": "DEFAULT"
  }
}
        order = orders.OrderCreate(accountID=accountID, data=datax)
        client.request(order)

        order_details = order.response
        return order_details


def Execution_details(order_details):
    """Converts a JSON trade confirmation into a readable string

    Parameters:
    order details (json): The JSON response from oanda.

    Returns:
    str: The trade confirmation in string format.
    """

    fil = order_details

    fil_type = fil["orderFillTransaction"]["type"]
    fil_execution_time = fil["orderFillTransaction"]["time"].replace("T", " ")
    fil_transid = fil["orderFillTransaction"]["requestID"]
    fil_account = fil["orderFillTransaction"]["accountID"]
    fil_id = fil["orderFillTransaction"]["orderID"]

    fil_instrument = fil["orderFillTransaction"]["instrument"]
    fil_units = fil["orderFillTransaction"]["units"]
    fil_price = fil["orderFillTransaction"]["price"]
    fil_profit = fil["orderFillTransaction"]["pl"]

    fil_information = " {}\n Execution Time: {}\n Request ID: {}\n Account ID: {}\n Order ID: {}\n\n Instrument: {}\n Units: {}\n Price: {}\n Gain/Loss: {}".format(fil_type, fil_execution_time,
    fil_transid, fil_account, fil_id, fil_instrument, fil_units, fil_price, fil_profit)

    return fil_information


def Open_positions(detail):
    """Request the open positions on the oanda account

    Parameters:
    detail (str): a basic dataframe or a detailed dataframe.

    Returns:
    dataframe: a dataframe with 2 columns or a dataframe with all columns.
    """

    current_positions = positions.OpenPositions(accountID=accountID)
    client.request(current_positions)
    position_info = current_positions.response
    position_details = position_info["positions"]
    list_positions = []

    for header in position_details:
        instrument = header["instrument"]
        instrument_name = instrument_names.get(instrument)
        if int(header["short"]["units"]) < 0:

            short_avg_price = header["short"]["averagePrice"]
            short_units = header["short"]["units"]
            short_pnl = header["short"]["pl"]
            short_unrel_pnl = header["short"]["unrealizedPL"]

            list_positions.append({"Instrument": instrument_name,
                                   "Units": short_units,
                                   "Average Price": short_avg_price,
                                   "Unrealised P&L": short_unrel_pnl,
                                   "P&L": short_pnl})

        elif int(header["long"]["units"]) > 0:

            long_avg_price = header["long"]["averagePrice"]
            long_units = header["long"]["units"]
            long_pnl = header["long"]["pl"]
            long_unrel_pnl = header["long"]["unrealizedPL"]

            list_positions.append({"Instrument": instrument_name,
                                   "Units": long_units,
                                   "Average Price": long_avg_price,
                                   "Unrealised P&L": long_unrel_pnl,
                                   "P&L": long_pnl})

        else:
            pass

    positions_dataframe = pd.DataFrame(list_positions)

    positions_dataframe = positions_dataframe[["Instrument", "Units", "Average Price", "Unrealised P&L", "P&L"]]

    if detail == "basic":
        orders_dataframe = positions_dataframe[["Instrument", "Units"]]
        return orders_dataframe
    elif detail == "advanced":
        return positions_dataframe
    else:
        pass
