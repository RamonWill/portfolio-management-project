import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import sqlite3

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


def Oanda_acc_summary():
    """Request the account details from oanda and return a dataframe."""
    account_details = accounts.AccountDetails(accountID)
    client.request(account_details)

    account_data = account_details.response

    df_account = pd.DataFrame(account_data).loc[["NAV", "balance", "currency"]]
    df_account = df_account.drop(["lastTransactionID"], axis=1)

    df_account.reset_index(inplace=True)

    return df_account


def get_instruments():
    """Gets a list of all tradable instruments on the Oanda platform."""
    account_instruments = accounts.AccountInstruments(accountID)
    client.request(account_instruments)
    account_instruments = account_instruments.response

    all_instruments = account_instruments["instruments"]

    names = [instrument["name"] for instrument in all_instruments]
    display_names = [instrument["displayName"] for instrument in all_instruments]

    if len(names) == len(display_names):
        instrument_pairs = {name: display_name for name, display_name
                            in zip(names, display_names)}
    try:
        return instrument_pairs
    except NameError:
        print("Error. Do all instrument names have display names?")


def load_instruments():
    """
    Stores instruments from the Oanda platform to the source database if they
    do not already exist in the database.
    """
    all_instruments = get_instruments()

    conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS Instruments
                 (name TEXT, displayName TEXT)""")

    db_names = [name[0] for name in c.execute("SELECT name FROM Instruments")]
    for names, display_names in all_instruments.items():
        if names in db_names:
            pass
        else:
            print(names, display_names)
            c.execute("""INSERT INTO Instruments
                         VALUES (:name, :displayName)""",
                      {"name": names, "displayName": display_names})

    conn.commit()
    c.close()
    conn.close()


def get_db_instruments():
    """ Extracts a list of all instruments from the source database."""
    conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""SELECT name, displayName
                 FROM Instruments
                 ORDER BY displayName""")

    instrument_table = c.fetchall()
    db_names = [row["name"] for row in instrument_table]
    db_display_names = [row["displayName"] for row in instrument_table]
    instrument_pairs = {name: display_name for name, display_name in
                        zip(db_names, db_display_names)}

    conn.commit()
    c.close()
    conn.close()

    return instrument_pairs


def Oanda_prices():
    """Request instrument prices from oanda and return a dataframe."""
    instrument_names = get_db_instruments()
    instrument_keys = list(instrument_names.keys())
    instrument_keys_sorted = ",".join(instrument_keys)

    params_prices = {"instruments": instrument_keys_sorted}
    pricing_details = pricing.PricingInfo(accountID=accountID,
                                          params=params_prices)
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

    return dataframe_prices


def Market_order(units, instrument):
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

    instrument_names = get_db_instruments()
    oanda_instrument = None

    for keys, values in instrument_names.items():
        if instrument == values:
            oanda_instrument = keys
    if oanda_instrument is None:
        print("{} is not a tradeable instrument".format(instrument))
        return "{}".format(instrument)

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
    if isinstance(fil, str):
        return "{} is not a tradeable instrument".format(fil)
    try:
        fil_type = fil["orderFillTransaction"]["type"]
        fil_time = fil["orderFillTransaction"]["time"].replace("T", " ")
        fil_transid = fil["orderFillTransaction"]["requestID"]
        fil_account = fil["orderFillTransaction"]["accountID"]
        fil_id = fil["orderFillTransaction"]["orderID"]

        fil_instrument = fil["orderFillTransaction"]["instrument"]
        fil_units = fil["orderFillTransaction"]["units"]
        fil_price = fil["orderFillTransaction"]["price"]
        fil_profit = fil["orderFillTransaction"]["pl"]
        details = (fil_type, fil_time, fil_transid, fil_account,
                   fil_id, fil_instrument, fil_units, fil_price, fil_profit)

        fil_information = (" {}\n Execution Time: {}\n Request ID: {}\n "
        "Account ID: {}\n Order ID: {}\n\n Instrument: {}\n Units: {}\n "
        "Price: {}\n Gain/Loss: {}").format(*details)

    except KeyError:
        fil_type = fil["orderCancelTransaction"]["type"]
        fil_reason = fil["orderCancelTransaction"]["reason"]
        fil_account = fil["orderCancelTransaction"]["accountID"]
        fil_id = fil["orderCancelTransaction"]["orderID"]

        fil_time = fil["orderCancelTransaction"]["time"].replace("T", " ")
        fil_instrument = fil["orderCreateTransaction"]["instrument"]
        fil_units = fil["orderCreateTransaction"]["units"]
        details = (fil_type, fil_reason, fil_account, fil_id,
                   fil_time, fil_instrument, fil_units)

        fil_information = (" {}\n Order Cancel Reason: {}\n "
        "Account ID: {}\n Order ID: {}\n\n Cancellation Time: {}\n "
        "Instrument: {}\n Units: {}\n").format(*details)
    return fil_information


def Open_positions(detail="basic"):
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
    instrument_names = get_db_instruments()

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
    try:
        if detail == "basic":
            orders_dataframe = positions_dataframe[["Instrument", "Units"]]
            return orders_dataframe
        elif detail == "advanced":
            return positions_dataframe
        else:
            pass
    except KeyError:
        print("There is a KeyError. Are the positions empty?")
