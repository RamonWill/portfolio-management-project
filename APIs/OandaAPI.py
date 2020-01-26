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
    try:
        oanda_instrument = next(k for k, v in instrument_names.items() if v == instrument)
    except StopIteration:
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
        time = fil["orderFillTransaction"]["time"].replace("T", " ")
        transid = fil["orderFillTransaction"]["requestID"]
        account = fil["orderFillTransaction"]["accountID"]
        id = fil["orderFillTransaction"]["orderID"]

        instrument = fil["orderFillTransaction"]["instrument"]
        units = fil["orderFillTransaction"]["units"]
        price = fil["orderFillTransaction"]["price"]
        profit = fil["orderFillTransaction"]["pl"]
        details = (fil_type, time, transid, account,
                   id, instrument, units, price, profit)

        fil_information = (" {}\n Execution Time: {}\n Request ID: {}\n "
        "Account ID: {}\n Order ID: {}\n\n Instrument: {}\n Units: {}\n "
        "Price: {}\n Gain/Loss: {}").format(*details)

    except KeyError:
        fil_type = fil["orderCancelTransaction"]["type"]
        reason = fil["orderCancelTransaction"]["reason"]
        account = fil["orderCancelTransaction"]["accountID"]
        id = fil["orderCancelTransaction"]["orderID"]

        time = fil["orderCancelTransaction"]["time"].replace("T", " ")
        instrument = fil["orderCreateTransaction"]["instrument"]
        units = fil["orderCreateTransaction"]["units"]
        details = (fil_type, reason, account, id,
                   time, instrument, units)

        fil_information = (" {}\n Order Cancel Reason: {}\n "
        "Account ID: {}\n Order ID: {}\n\n Cancellation Time: {}\n "
        "Instrument: {}\n Units: {}\n").format(*details)
    return fil_information


def trade_to_db(order_details):
    """Stores the trade details into a sqlite3 database.

    Parameters:
    order details (json): The JSON response from oanda.
    """

    fil = order_details
    if isinstance(fil, str):
        pass
    else:
        try:
            id = fil["orderFillTransaction"]["orderID"]
            instrument = fil["orderFillTransaction"]["instrument"]
            units = fil["orderFillTransaction"]["units"]
            price = fil["orderFillTransaction"]["price"]
            profit = fil["orderFillTransaction"]["pl"]

            instrument_names = get_db_instruments()
            instrument = instrument_names.get(instrument)

            return add_to_db(instrument, units, price, id, profit, cancelled=0)

        except KeyError:
            # I should return this instead
            print("""The transaction was cancelled.\n
                     Therefore nothing was saved to the database.""")


def get_largest_positions():
    conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")
    query = """SELECT name, SUM(quantity*price) as 'MarketVal'
                FROM All_Transactions
                WHERE cancelled = 0
                GROUP BY name
                ORDER BY ABS(SUM(quantity*price))DESC
                LIMIT 5"""

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_all_positions():
    conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")
    query = """SELECT *
               FROM All_Transactions;"""
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


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

def validate_entry(name, quantity, price):
    instruments = get_db_instruments()
    try:
        p = next(True for key, value in instruments.items() if value == name)
        quantity = float(quantity)
        check_price = (float(price) >= 0)
    except (StopIteration, ValueError) as e:
        if (isinstance(e, StopIteration)):
            return "The name you have entered is not a tradeable instrument."
        elif(isinstance(e, ValueError)):
            return "The Quantity and Price must be valid numbers."

    if not check_price:
        return "The Price cannot be a negative number"
    else:
        return True


def generateID():
    conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")
    c = conn.cursor()
    c.execute("""SELECT MAX(TRIM(id, 'C'))
                 FROM all_transactions
                 WHERE id LIKE 'C%' """)
    last_id = c.fetchone()[0]

    if last_id is None:
        new_id = "C{:04n}".format(1)
    else:
        new_id = "C{:04n}".format(int(last_id)+1)
    print(new_id)

    conn.commit()
    c.close()
    conn.close()

    return new_id

def cancelled_toggle(id, toggle):
    conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")

    c = conn.cursor()
    c.execute("""UPDATE all_transactions
                 SET cancelled = ?
                 WHERE id = ?""", (toggle, id))

    result = c.rowcount
    conn.commit()
    c.close()
    conn.close()
    if result == 0:
        return "Order ID does not exist in the database.".format(id)
    else:
        return "Changes have been made to Order ID {}.".format(id)


def add_to_db(instrument, units, price, id=None, cancelled=0, profit=0):
    if id is None:
        id = generateID()

    conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS All_Transactions
                 (id TEXT, name TEXT, quantity REAL, price REAL, pnl REAL, cancelled INTEGER)""")
    placeholders = {"id": id,
                    "name": instrument,
                    "quantity": units,
                    "price": price,
                    "pnl": profit,
                    "cancelled": 0
                    }
    c.execute("""INSERT INTO All_Transactions
                 VALUES (:id, :name, :quantity, :price, :pnl, :cancelled)""",
              placeholders)
    conn.commit()
    c.close()
    conn.close()
    return "Order ID {} stored to the database".format(id)
