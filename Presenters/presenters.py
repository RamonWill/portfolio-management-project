import sys
from pathlib import Path
from collections import namedtuple

PARENT_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT_PATH))
import Core.OandaAPI as OandaAPI
from Core.NewsAPI import latest_news
from Core.DatabaseConnections import PRMS_Database
from Core.VantageAlphaAPI import AV_FXData


class HomePage(object):

    def __init__(self, view):
        super().__init__()
        self.View = view

    def create_pie_data(self):
        try:
            with PRMS_Database() as db:
                df = db.get_largest_positions()
                names = df["name"]
        except TypeError:
            return None  # positions are empty

        market_vals = abs(df["MarketVal"])
        data = {"market_values": market_vals, "names": names}
        self.View.draw_pie_chart(data=data)

    def create_tables(self):
        Tables = namedtuple("Tables", ("account", "prices", "news"))
        account = OandaAPI.Oanda_acc_summary()
        account_rows = account.to_numpy().tolist()
        price_rows = OandaAPI.Oanda_prices()
        news_rows = latest_news()
        T = Tables(account_rows, price_rows, news_rows)
        self.View.update_tables(Tables=T)

    def create_rec_summary(self):
        rec = OandaAPI.Reconciliation()
        info = rec.num_matches()
        self.View.update_rec_summary(text=info)


class CreateOrders(object):

    def __init__(self, view):
        self.View = view

    def create_positions(self):
        try:
            positions = OandaAPI.Open_positions("basic")
            position_rows = positions.to_numpy().tolist()
        except AttributeError:
            return None
        self.View.update_positions(rows=position_rows)

    def execute_trade(self, units, instrument, acknowledged=False):
        if not acknowledged:
            info = "The trade is not acknowledged.\nYour order has not been sent."
        else:
            order_details = OandaAPI.Market_order(units, instrument)
            OandaAPI.trade_to_db(order_details)
            info = OandaAPI.Execution_details(order_details)

        self.View.clear_entries()
        self.View.display_order_info(text=info)
        self.View.refresh_positions()


class SecurityPrices(object):

    def __init__(self, view):
        self.View = view

    def create_chart(self, period, indicator, currency1, currency2):
        Chart = AV_FXData(period, currency1, currency2, indicator)
        Chart_data = Chart.Fx_chart_gui()

        Chart_prices = Chart_data.tail(4)  # gets the 4 most recent prices
        Chart_prices = Chart_prices[["Date", "Close Price"]]
        prices = Chart_prices.to_numpy().tolist()

        self.View.draw_chart(data=Chart_data, indicator=indicator)
        self.View.clear_prices()
        self.View.display_prices(rows=prices)


class CurrentPositions(object):

    def __init__(self, view):
        self.View = view

    def create_positions(self):
        try:
            positions = OandaAPI.Open_positions("advanced")
            position_rows = positions.to_numpy().tolist()
        except AttributeError:
            return None
        self.View.update_positions(rows=position_rows)


class PositionReconciliation(object):

    def __init__(self, view):
        self.View = view

    def create_rec(self):
        self.View.clear_table()
        rec = OandaAPI.Reconciliation()
        rec_table = rec.generate_rec()
        rec_table_rows = rec_table.to_numpy().tolist()
        self.View.update_table(rows=rec_table_rows)
