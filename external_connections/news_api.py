import requests
import json
from external_connections.ConnectionObject import ConnectionObject


class NewsConnection(object):
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.connection_status = False
        self._get_status()

    def _get_status(self):
        uri = "https://newsapi.org/v2/sources?"
        params = {"apiKey": self.api_key}
        response = requests.get(uri, params=params)
        self.connection_status = response.ok

    def latest_headlines(self, category="business", country="us"):
        if not self.connection_status:
            return []

        uri = "https://newsapi.org/v2/top-headlines?"
        params = {
            "apiKey": self.api_key,
            "category": category,
            "country": country,
            "pageSize": 20,
        }
        response = requests.get(uri, params=params)
        all_headlines = response.json()
        p = json.loads(response.content)
        articles = []
        for headline in all_headlines["articles"]:
            source = headline["source"]["name"]
            title = headline["title"]
            url = headline["url"]
            article = Articles(source, title, url)
            articles.append(article)
        return articles


class Articles(ConnectionObject):
    def __init__(self, source, title, url):
        self.source = source
        self.title = title
        self.url = url

    def __repr__(self):
        return f"{self.source}: {self.title}"
