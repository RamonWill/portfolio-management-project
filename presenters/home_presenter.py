from custom_objects import Reconciliation
import pandas as pd


class HomePresenter(object):
    def __init__(self, view, db, news, oanda):
        self.view = view
        self._db = db
        self._news = news
        self._oanda = oanda

    def get_homepage_data(self):
        news_articles = self._news.latest_headlines()
        account_summary = self._oanda.account_summary()
        stored_instruments = self._db.get_db_instruments()
        instrument_keys = list(stored_instruments.keys())
        sorted_keys = ",".join(instrument_keys)  # A sorted string
        tradeable_instruments = self._oanda.get_live_prices(instruments=sorted_keys)
        self.view.display_data(news_articles, account_summary, tradeable_instruments)

        oanda_positions = self._oanda.live_positions(detail="advanced")
        prms_positions = self._db.get_db_positions()
        rec = Reconciliation(oanda_positions, prms_positions)
        rec_status = rec.num_matches()
        self.view.display_rec_status(rec_status)

    def create_pie_data(self):
        pie_data = self._db.get_largest_positions()
        df_pie_data = pd.DataFrame([vars(header) for header in pie_data])
        self.view.draw_pie_chart(df_pie_data)
