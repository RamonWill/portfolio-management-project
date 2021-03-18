from oandapyV20 import API
from oandapyV20.endpoints import accounts, pricing, orders, positions
from oandapyV20.exceptions import V20Error
from external_connections.ConnectionObject import ConnectionObject
# documentation - https://oanda-api-v20.readthedocs.io/en/latest/

class OandaConnection(object):
    def __init__(self, api_key="", account_id=""):
        self.account_id = account_id
        self.api_client = API(access_token=api_key)
        self.connection_status = False
        self.BASE_URL = "https://api-fxpractice.oanda.com"
        self._get_status()

    def _get_status(self):
        try:
            account_details = accounts.AccountDetails(self.account_id)
            self.api_client.request(account_details)
            self.connection_status=True
        except V20Error:
            self.connection_status = False

    def account_summary(self):
        account_details = accounts.AccountDetails(self.account_id)
        self.api_client.request(account_details)
        account_data = account_details.response
        nav = account_data["account"]["NAV"]
        balance = account_data["account"]["balance"]
        currency = account_data["account"]["currency"]
        summary = AccountSummary(nav=nav, balance=balance, currency=currency)

        return summary

    def get_instruments(self):
        """Gets a list of all tradable instruments on the Oanda platform."""
        account_instruments = accounts.AccountInstruments(self.account_id)
        self.api_client.request(account_instruments)
        account_instruments = account_instruments.response

        all_instruments = account_instruments["instruments"]

        instrument_pairs = {i["name"]: i["displayName"] for i in all_instruments}
        return instrument_pairs

    def get_live_prices(self, instruments):
        if not self.connection_status or len(instruments)==0:
            return []

        params_prices = {"instruments": instruments}
        pricing_details = pricing.PricingInfo(accountID=self.account_id,
                                              params=params_prices)
        self.api_client.request(pricing_details)
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

class AccountSummary(ConnectionObject):
    def __init__(self, nav=None, balance=None, currency=None):
        self.nav = nav
        self.balance = float(balance)
        self.currency = currency

class OandaPrices(ConnectionObject):
    def __init__(self, instrument=None, bid=None, ask=None):
        self.instrument = instrument
        self.bid = float(bid)
        self.ask = float(ask)