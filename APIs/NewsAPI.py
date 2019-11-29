import requests
import pandas as pd

try:
    import config
except ImportError:
    import APIs.config as config

api_key = config.news_key


def latest_news_headlines():
    """Request bloomberg articles from News API and return a dataframe"""

    url = "https://newsapi.org/v2/top-headlines?"

    params = {"apiKey": api_key,
              "sources": "bloomberg",
              "pagesize": 10}

    response = requests.get(url, params=params)
    news = response.json()
    news_articles = news["articles"]
    formatted_articles = []

    for article in news_articles:
        source = article["source"]["name"]
        headline = "{}...".format(article["title"][0:46])
        link = article["url"]
        formatted_articles.append({"Source": source,
                                   "Title": headline,
                                   "Link": link})

    news_dataframe = pd.DataFrame(formatted_articles)
    news_dataframe = news_dataframe[["Title", "Source", "Link"]]
    # pd.set_option('display.max_columns', 3)

    return news_dataframe
