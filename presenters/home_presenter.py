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
        pass
