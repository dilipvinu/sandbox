import sys
from newspaper import Article


def get_text(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article.text, article.summary


if __name__ == "__main__":
    url = sys.argv[1]
    text, summary = get_text(url)
    print(text.encode('utf-8'))
    print('==========')
    print(summary.encode('utf-8'))
