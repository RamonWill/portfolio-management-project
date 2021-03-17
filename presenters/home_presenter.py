class HomePresenter(object):
    def __init__(self, view, db, news):
        self.view = view
        self._db = db
        self._news = news

    def get_homepage_data(self):
        news_articles = self._news.latest_headlines()
        self.view.display_data(news_articles)
        pass
