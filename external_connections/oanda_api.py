from oandapyV20 import API
from oandapyV20.endpoints import accounts, pricing, orders, positions
from oandapyV20.exceptions import V20Error
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
        summary = [["NAV", nav],
                           ["Balance", balance],
                           ["Currency", currency]]

        return summary

    def get_instruments(self):
        """Gets a list of all tradable instruments on the Oanda platform."""
        account_instruments = accounts.AccountInstruments(self.account_id)
        self.api_client.request(account_instruments)
        account_instruments = account_instruments.response

        all_instruments = account_instruments["instruments"]

        instrument_pairs = {i["name"]: i["displayName"] for i in all_instruments}
        return instrument_pairs

x = OandaConnection("96732e2978c2339ada31ef16971308fd-5ef54f7a26646a169d04a02befb786ca", "101-004-18515982-001")