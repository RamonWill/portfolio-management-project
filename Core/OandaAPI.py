import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions

# documentation - https://oanda-api-v20.readthedocs.io/en/latest/
# the import error exception is raised if i run this file from prmsystem_api

try:
    import config
    from DatabaseConnections import PRMS_Database
except ImportError:
    import Core.config as config
    from Core.DatabaseConnections import PRMS_Database


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
    Stores new instruments from the Oanda platform to the source database if
    they do not already exist in the database.
    """
    all_instruments = get_instruments()

    with PRMS_Database() as db:
        db_instruments = db.get_db_instruments()
        db_names = db_instruments.keys()

        for name, display_name in all_instruments.items():
            if name in db_names:
                pass
            else:
                print(name, display_name)
                db.load_instruments(name, display_name)
    print("Complete")


def Oanda_prices():
    """Request instrument prices from oanda and return a dataframe."""

    with PRMS_Database() as db:
        instrument_names = db.get_db_instruments()

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
        list_prices.append([instrument_name,
                            bid_price,
                            ask_price])

    return list_prices


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
    with PRMS_Database() as db:
        instrument_names = db.get_db_instruments()

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

            with PRMS_Database() as db:
                instrument_names = db.get_db_instruments()
                instrument = instrument_names.get(instrument)
                message = db.add_to_db(instrument, units, price, id, profit)
                return message

        except KeyError:
            # I should return this instead
            print("""The transaction was cancelled.\n
                     Therefore nothing was saved to the database.""")


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
    with PRMS_Database() as db:
        instrument_names = db.get_db_instruments()


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


class Reconciliation(object):
    def __init__(self):
        self.oanda_pos = None
        self.prms_pos = None

    def generate_rec(self):
        self.populate_tables()

        rec = self.oanda_pos.merge(self.prms_pos, on="Instrument", how="outer")
        rec = rec[["Instrument", "Units",
                   "PRMS Units", "Avg Price",
                   "PRMS Avg Price"]]
        rec["Position Diff"] = rec["Units"] - rec["PRMS Units"]
        rec["Price Diff"] = rec["Avg Price"] - rec["PRMS Avg Price"]

        commentary = []

        for row in rec.itertuples():
            position_diff = row[6]
            price_diff = row[7]
            if position_diff == 0 and price_diff == 0:
                commentary.append("OK")
            elif position_diff == 0 and price_diff != 0:
                commentary.append("Price Break")
            elif position_diff !=0 and price_diff == 0:
                commentary.append("Position Break")
            else:
                commentary.append("Position and Price Break")

        rec["Commentary"] = commentary
        return rec

    def num_matches(self):
        rec = self.generate_rec()
        total_records = len(rec)
        matches = len(rec.query("Commentary == 'OK'"))
        breaks = total_records - matches

        if total_records == matches:
            return "There are no position breaks"
        else:
            return "{} out of {}\npositions have breaks".format(breaks,
                                                                total_records)

    def populate_tables(self):
        self.oanda_pos = self.get_oanda_positions()
        self.prms_pos = self.get_prms_positions()

    def get_oanda_positions(self):
        pos = Open_positions("advanced")
        pos["Average Price"] = pos["Average Price"].astype(float)
        pos["Units"] = pos["Units"].astype(float)
        return pos.rename(columns={"Average Price": "Avg Price"})

    def get_prms_positions(self):
        with PRMS_Database() as db:
            positions = db.get_prms_positions()

        return positions
