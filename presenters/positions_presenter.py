class PositionsPresenter(object):
    def __init__(self, view, oanda):
        self.view = view
        self._oanda = oanda

    def get_live_positions(self):
        positions = self._oanda.live_positions(detail="advanced")
        self.view.display_positions(positions)
