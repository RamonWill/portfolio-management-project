class OrderPresenter(object):
    def __init__(self, view, db, oanda):
        self.view = view
        self._db = db
        self._oanda = oanda

    def get_live_positions(self):
        positions = self._oanda.live_positions(detail="basic")
        self.view.display_positions(positions)

    def execute_trade(self, units, instrument, acknowledged=False):
        if not acknowledged:
            info = "The trade is not acknowledged.\n" "Your order has not been sent."
        else:
            fill = self._oanda.market_order(units, instrument)
            self._db.record_trade(fill)
            info = self._oanda.execution_details(fill)
            self.get_live_positions()
        self.view.clear_entries()
        self.view.display_order_info(text=info)
