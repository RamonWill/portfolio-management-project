import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as Positions

# documentation - https://oanda-api-v20.readthedocs.io/en/latest/
# the import error exception is raised if i run this file from prmsystem_api

try:
    from config import Configurations
    from database_connections import PRMS_Database
except ImportError:
    from models.config import Configurations
    from models.database_connections import PRMS_Database


api_key = Configurations.OANDA_KEY
accountID = Configurations.OANDA_ACCOUNT
url = "https://api-fxpractice.oanda.com"

client = API(access_token=api_key)


def oanda_acc_summary():
    """Requests the account details from oanda"""
    account_details = accounts.AccountDetails(accountID)
    client.request(account_details)

    account_data = account_details.response
    nav = account_data["account"]["NAV"]
    balance = account_data["account"]["balance"]
    currency = account_data["account"]["currency"]
    account_details = [["NAV", nav],
                       ["Balance", balance],
                       ["Currency", currency]]

    return account_details


def get_instruments():
    """Gets a list of all tradable instruments on the Oanda platform."""
    account_instruments = accounts.AccountInstruments(accountID)
    client.request(account_instruments)
    account_instruments = account_instruments.response

    all_instruments = account_instruments["instruments"]

    instrument_pairs = {i["name"]: i["displayName"] for i in all_instruments}
    return instrument_pairs


def load_instruments():
    """
    Stores new instruments from the Oanda platform to the source database if
    they do not already exist in the database.
    """
    all_instruments = get_instruments()
    count = 0
    with PRMS_Database() as db:
        db_instruments = db.get_db_instruments()
        db_names = set(db_instruments.keys())
        print(db_names)
        for name, display_name in all_instruments.items():
            if name not in db_names:
                db.updates_instruments(name, display_name)
                print(name, display_name)
                count += 1
    print(f"Completed. {count} item(s) added to the database.")


def oanda_prices():
    """Request instrument prices from oanda."""

    with PRMS_Database() as db:
        instrument_names = db.get_db_instruments()

    instrument_keys = list(instrument_names.keys())
    instrument_keys_sorted = ",".join(instrument_keys)  # A sorted string

    params_prices = {"instruments": instrument_keys_sorted}
    pricing_details = pricing.PricingInfo(accountID=accountID,
                                          params=params_prices)
    client.request(pricing_details)
    pricing_details = pricing_details.response
    pricing_details = pricing_details["prices"]

    list_prices = []

    for header in pricing_details:
        instrument = header["instrument"]
        name = instrument_names.get(instrument)
        bid_price = header["bids"][0]["price"]
        ask_price = header["asks"][0]["price"]
        list_prices.append([name,
                            bid_price,
                            ask_price])

    return list_prices


def market_order(units, instrument):
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
        print(f"'{instrument}' is not a tradeable instrument")
        return f"{instrument}"

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


def fil_success(fil):
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

    fil_information = ("{}\n"
                       "Execution Time: {}\n"
                       "Request ID: {}\n"
                       "Account ID: {}\n"
                       "Order ID: {}\n\n"
                       "Instrument: {}\n"
                       "Units: {}\n"
                       "Price: {}\n"
                       "Gain/Loss: {}").format(*details)

    return fil_information


def fil_cancellation(fil):
    fil_type = fil["orderCancelTransaction"]["type"]
    reason = fil["orderCancelTransaction"]["reason"]
    account = fil["orderCancelTransaction"]["accountID"]
    id = fil["orderCancelTransaction"]["orderID"]

    time = fil["orderCancelTransaction"]["time"].replace("T", " ")
    instrument = fil["orderCreateTransaction"]["instrument"]
    units = fil["orderCreateTransaction"]["units"]
    details = (fil_type, reason, account, id,
               time, instrument, units)

    fil_information = ("{}\n"
                       "Order Cancel Reason: {}\n"
                       "Account ID: {}\n"
                       "Order ID: {}\n\n"
                       "Cancellation Time: {}\n"
                       "Instrument: {}\n"
                       "Units: {}\n").format(*details)
    return fil_information


def execution_details(order_details):
    """Converts a JSON trade confirmation into a readable string

    Parameters:
    order details (json): The JSON response from oanda.

    Returns:
    str: The trade confirmation in string format.
    """

    fil = order_details
    if isinstance(fil, str):
        return f"{fil} is not a tradeable instrument"

    if "orderFillTransaction" in fil:
        fil_information = fil_success(fil)
    else:
        fil_information = fil_cancellation(fil)

    return fil_information


def trade_to_db(order_details):
    """Stores the trade details into a sqlite3 database.

    Parameters:
    order details (json): The JSON response from oanda.
    """

    fil = order_details
    if not isinstance(fil, str):
        if "orderFillTransaction" in fil:
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

        else:
            message = "The transaction was cancelled.\n"
            return message
    else:
        return None


def live_positions(detail="basic"):
    """Request the open positions on the oanda account

    Parameters:
    detail (str): a basic matrix or the full matrix.

    Returns:
    dataframe: a matrix with 2 columns or a matrix withall columns.
    """

    current_positions = Positions.OpenPositions(accountID=accountID)
    client.request(current_positions)
    position_info = current_positions.response
    positions = position_info["positions"]
    with PRMS_Database() as db:
        instrument_names = db.get_db_instruments()

    position_details = []
    for position in positions:
        instrument = position["instrument"]
        instrument_name = instrument_names.get(instrument)

        if int(position["short"]["units"]) < 0:
            position_data = position["short"]

        elif int(position["long"]["units"]) > 0:
            position_data = position["long"]

        avg_price = position_data["averagePrice"]
        units = position_data["units"]
        pnl = position_data["pl"]
        unrel_pnl = position_data["unrealizedPL"]

        data = [instrument_name, units, avg_price, unrel_pnl, pnl]
        position_details.append(data)

    if len(position_details) == 0:
        print("There are no positions")
        return None

    if detail == "basic":
        return [row[0:2] for row in position_details]  # instrument name, units
    elif detail == "advanced":
        return position_details
    else:
        raise TypeError("detail should be 'basic' or 'advanced'")


class Reconciliation(object):
    def __init__(self):
        self.oanda_pos = None
        self.prms_pos = None

    def generate_rec(self):
        self.populate_tables()
        if self.oanda_pos is None:
            return None

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
            elif position_diff != 0 and price_diff == 0:
                commentary.append("Position Break")
            else:
                commentary.append("Position and Price Break")

        rec["Commentary"] = commentary
        return rec

    def num_matches(self):
        rec = self.generate_rec()
        if rec is None:
            return "There are no positions"
        total_records = len(rec)
        matches = len(rec.query("Commentary == 'OK'"))
        breaks = total_records - matches

        if total_records == matches:
            return "There are no position breaks"
        else:
            return f"{breaks} out of {total_records}\npositions have breaks"

    def populate_tables(self):
        self.oanda_pos = self.get_oanda_positions()
        self.prms_pos = self.get_prms_positions()

    def get_oanda_positions(self):
        data = live_positions("advanced")
        if not data:
            return None

        headers = ["Instrument", "Units", "Average Price", "Unrealised P&L",
                   "P&L"]

        pos = pd.DataFrame.from_records(data, columns=headers)
        pos["Average Price"] = pos["Average Price"].astype(float)
        pos["Units"] = pos["Units"].astype(float)
        return pos.rename(columns={"Average Price": "Avg Price"})

    def get_prms_positions(self):
        with PRMS_Database() as db:
            positions = db.get_prms_positions()

        return positions
