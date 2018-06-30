import sys
from readability.readability import Document
import urllib.request


def get_summary(url):
    html = urllib.request.urlopen(url).read()
    doc = Document(html)
    doc.parse(["summary", "short_title"])
    readable_article = doc.summary()
    readable_title = doc.short_title()
    return readable_article, readable_title


if __name__ == "__main__":
    url = sys.argv[1]
    summary, title = get_summary(url)
    print(title.encode('utf-8'))
    print('==========')
    print(summary.encode('utf-8'))
