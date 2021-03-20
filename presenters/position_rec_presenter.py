from custom_objects import Reconciliation


class PositionRecPresenter(object):
    def __init__(self, view, db, oanda):
        self.view = view
        self._db = db
        self._oanda = oanda

    def reconcile_positions(self):
        oanda_positions = self._oanda.live_positions(detail="advanced")
        prms_positions = self._db.get_db_positions()
        rec = Reconciliation(oanda_positions, prms_positions)
        df_reconciled_positions = rec.generate_rec()
        self.view.display_reconciled_positions(df_reconciled_positions)
