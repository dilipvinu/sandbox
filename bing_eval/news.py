import socket
import sys
import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.request import urlopen
from urllib.error import HTTPError
from textblob import TextBlob
from urllib.parse import urlparse

URL = "https://api.cognitive.microsoft.com/bing/v7.0/news/search"
KEY = "840db9772c494744b0e1bb1ac69b9279"
KEY2 = "6c8b3f301950436b8d36647d263a0573"


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def get_sentiment(url, query):
    print("Analyzing {}".format(url))
    try:
        html = urlopen(url, timeout=5)
        text = text_from_html(html)
        article = TextBlob(text)
        print("{} sentences".format(len(article.sentences)))
        for sentence in article.sentences:
            if query in sentence.lower() and sentence.sentiment.polarity > 0.1:
                print(sentence.string.encode('utf-8'))
        return article.sentiment.polarity
    except HTTPError:
        print("Error for url {}".format(url))
        return 0
    except socket.timeout:
        print("Timeout for url {}".format(url))
        return 0


def eligible_news(item):
    uri = urlparse(item["url"])
    if uri.netloc.endswith('org') or uri.netloc.endswith('edu'):
        return False
    return True


def get_news(query, category):
    headers = {'Ocp-Apim-Subscription-Key': KEY,
               # 'Accept-Language': 'EN'
               }
    params = {'q': '"' + query + '" AND "' + category + '"',
              # 'q': '"' + query + '" AND "' + category + '" loc:AU',
              'safeSearch': 'Strict',
              'setLang': 'EN',
              'freshness': 'Day',
              'mkt': 'en-au',
              # 'cc': 'in'
              }
    response = requests.get(URL, headers=headers, params=params)
    return json.loads(response.text)


if __name__ == "__main__":
    query = sys.argv[1]
    category = sys.argv[2]
    results = get_news(query, category)
    news = results["value"]
    print("{} results".format(len(news)))
    news = list(filter(eligible_news, news))
    print("{} eligible results".format(len(news)))
    count = 0
    for item in news:
        # print(item["name"].encode('utf-8'))
        url = item["url"]
        sentiment = get_sentiment(item["url"], query)
        if sentiment > 0.15:
            count += 1
    print("{} positive articles".format(count))
