import requests
import pandas as pd

try:
    import config
except ImportError:
    import APIs.config as config
#This is the financial news dataframe on the homepage
api_key = config.news_key


def latest_news_headlines():
    """Request bloomberg articles from News API and return a dataframe"""
    url_news = "https://newsapi.org/v2/top-headlines?"

    params_news = {"apiKey":api_key,
    "sources":"bloomberg", "pagesize":10}

    response_news = requests.get(url_news, params=params_news)

    latest_news = response_news.json()

    latest_news_articles = latest_news["articles"]


    latest_news_articles_formatted = []
    #next reiterate through the data and populate it into a dataframe
    for item in latest_news_articles:
        latest_news_articles_formatted.append({"Source":item["source"]["name"],
        "Title":"{}...".format(item["title"][0:46]), "Link":item["url"]})

    latest_news_articles_dataframe = pd.DataFrame(latest_news_articles_formatted)
    latest_news_articles_dataframe = latest_news_articles_dataframe[["Title", "Source", "Link"]]
    pd.set_option('display.max_columns', 3)


    return latest_news_articles_dataframe
