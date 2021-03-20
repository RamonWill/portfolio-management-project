from oandapyV20 import API
from oandapyV20.endpoints import accounts, pricing, orders, positions
from oandapyV20.exceptions import V20Error
from external_connections.ConnectionObject import ConnectionObject

# documentation - https://oanda-api-v20.readthedocs.io/en/latest/


class OandaConnection(object):
    def __init__(self, api_key="", account_id=""):
        self._account_id = account_id
        self._api_client = API(access_token=api_key)
        self.connection_status = False
        self.BASE_URL = "https://api-fxpractice.oanda.com"
        self._get_status()

    def _get_status(self):
        try:
            account_details = accounts.AccountDetails(self._account_id)
            self._api_client.request(account_details)
            self.connection_status = True
        except V20Error:
            self.connection_status = False

    def account_summary(self):
        if not self.connection_status:
            return []
        account_endpoint = accounts.AccountDetails(self._account_id)
        self._api_client.request(account_endpoint)
        account_data = account_endpoint.response
        nav = account_data["account"]["NAV"]
        balance = account_data["account"]["balance"]
        currency = account_data["account"]["currency"]
        summary = AccountSummary(nav=nav, balance=balance, currency=currency)

        return summary

    def get_instruments(self):
        """Gets a list of all tradable instruments on the Oanda platform."""
        instruments_endpoint = accounts.AccountInstruments(self._account_id)
        self._api_client.request(instruments_endpoint)
        instruments = instruments_endpoint.response

        all_instruments = instruments["instruments"]

        instrument_pairs = {i["name"]: i["displayName"] for i in all_instruments}
        return instrument_pairs

    def get_live_prices(self, instruments):
        if not self.connection_status or len(instruments) == 0:
            return []

        params_prices = {"instruments": instruments}
        pricing_details = pricing.PricingInfo(
            accountID=self._account_id, params=params_prices
        )
        self._api_client.request(pricing_details)
        pricing_details = pricing_details.response
        pricing_details = pricing_details["prices"]
        all_prices = []
        for header in pricing_details:
            name = header["instrument"]
            ask_price = header["asks"][0]["price"]
            bid_price = header["bids"][0]["price"]
            price = OandaPrices(instrument=name, ask=ask_price, bid=bid_price)
            all_prices.append(price)
        return all_prices

    def live_positions(self, detail="basic"):
        if not self.connection_status:
            return []
        position_endpoint = positions.OpenPositions(self._account_id)
        self._api_client.request(position_endpoint)
        response = position_endpoint.response
        current_positions = response["positions"]

        position_details = []
        # This violates DRY fix it
        if detail == "basic":
            for position in current_positions:
                instrument = position["instrument"]
                if int(position["short"]["units"]) < 0:
                    position_data = position["short"]

                elif int(position["long"]["units"]) > 0:
                    position_data = position["long"]
                units = position_data["units"]
                basic_position = OandaPositionsBasic(instrument, units)
                position_details.append(basic_position)

            return position_details
        elif detail == "advanced":
            for position in current_positions:
                instrument = position["instrument"]

                if int(position["short"]["units"]) < 0:
                    position_data = position["short"]

                elif int(position["long"]["units"]) > 0:
                    position_data = position["long"]

                avg_price = position_data["averagePrice"]
                units = position_data["units"]
                pnl = position_data["pl"]
                unrel_pnl = position_data["unrealizedPL"]
                advanced_position = OandaPositionsAdvanced(
                    instrument, units, avg_price, unrel_pnl, pnl
                )
                position_details.append(advanced_position)
            return position_details
        else:
            return None  # throw error in future

    def market_order(self, units, instrument):
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

        datax = {
            "order": {
                "units": units,
                "instrument": instrument,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT",
            }
        }
        order = orders.OrderCreate(accountID=self._account_id, data=datax)
        self._api_client.request(order)

        fill = order.response
        return fill

    def fill_success(self, fill):
        fill_type = fill["orderFillTransaction"]["type"]
        time = fill["orderFillTransaction"]["time"].replace("T", " ")
        transid = fill["orderFillTransaction"]["requestID"]
        account = fill["orderFillTransaction"]["accountID"]
        id = fill["orderFillTransaction"]["orderID"]

        instrument = fill["orderFillTransaction"]["instrument"]
        units = fill["orderFillTransaction"]["units"]
        price = fill["orderFillTransaction"]["price"]
        profit = fill["orderFillTransaction"]["pl"]
        details = (
            fill_type,
            time,
            transid,
            account,
            id,
            instrument,
            units,
            price,
            profit,
        )

        fill_information = (
            "{}\n"
            "Execution Time: {}\n"
            "Request ID: {}\n"
            "Account ID: {}\n"
            "Order ID: {}\n\n"
            "Instrument: {}\n"
            "Units: {}\n"
            "Price: {}\n"
            "Gain/Loss: {}"
        ).format(*details)

        return fill_information

    def fil_cancellation(self, fill):
        fill_type = fill["orderCancelTransaction"]["type"]
        reason = fill["orderCancelTransaction"]["reason"]
        account = fill["orderCancelTransaction"]["accountID"]
        id = fill["orderCancelTransaction"]["orderID"]

        time = fill["orderCancelTransaction"]["time"].replace("T", " ")
        instrument = fill["orderCreateTransaction"]["instrument"]
        units = fill["orderCreateTransaction"]["units"]
        details = (fill_type, reason, account, id, time, instrument, units)

        fill_information = (
            "{}\n"
            "Order Cancel Reason: {}\n"
            "Account ID: {}\n"
            "Order ID: {}\n\n"
            "Cancellation Time: {}\n"
            "Instrument: {}\n"
            "Units: {}\n"
        ).format(*details)
        return fill_information

    def execution_details(self, fill):
        """Converts a JSON trade confirmation into a readable string
        Parameters:
        order details (json): The JSON response from oanda.
        Returns:
        str: The trade confirmation in string format.
        """
        if isinstance(fill, str):
            return f"{fill} is not a tradeable instrument"

        if "orderFillTransaction" in fill:
            fill_information = self.fill_success(fill)
        else:
            fill_information = self.fill_cancellation(fill)

        return fill_information


class AccountSummary(ConnectionObject):
    def __init__(self, nav, balance, currency):
        self.nav = nav
        self.balance = float(balance)
        self.currency = currency


class OandaPrices(ConnectionObject):
    def __init__(self, instrument, bid, ask):
        self.instrument = instrument
        self.bid = float(bid)
        self.ask = float(ask)


class OandaPositionsBasic(ConnectionObject):
    def __init__(self, name, units):
        self.name = name
        self.units = float(units)


class OandaPositionsAdvanced(ConnectionObject):
    def __init__(self, name, units, avg_price, unrel_pnl, pnl):
        self.name = name
        self.units = float(units)
        self.avg_price = float(avg_price)
        self.unrel_pnl = float(unrel_pnl)
        self.pnl = float(pnl)
