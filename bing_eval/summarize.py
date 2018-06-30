from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

import sys

from pyteaser import SummarizeUrl
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = "english"
SENTENCES_COUNT = 1


def summarize_news(url):
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    document = parser.document
    summary = []
    for sentence in summarizer(document, SENTENCES_COUNT):
        summary.append(sentence._text)

    print(' '.join(summary).encode('utf-8'))
    print(document.paragraphs[0].sentences[0]._text)


def tease_url(url):
    summaries = SummarizeUrl(url)
    print(summaries)


if __name__ == "__main__":
    url = sys.argv[1]
    summarize_news(url)
    # tease_url(url)
