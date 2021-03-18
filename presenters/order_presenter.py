class OrderPresenter(object):
    def __init__(self, view, db, oanda):
        self.view = view
        self._db = db
        self._oanda = oanda

    def get_live_positions(self):
        positions = self._oanda.live_positions(detail="basic")
        self.view.display_positions(positions)