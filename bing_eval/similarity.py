import sys

import spacy
from article import get_text


def get_similarity(article1, article2, accuracy="low"):
    if accuracy == "high":
        name = "en_core_web_lg"
    elif accuracy == "medium":
        name = "en_core_web_md"
    else:
        name = "en_core_web_sm"
    nlp = spacy.load(name)
    doc1 = nlp(article1)
    doc2 = nlp(article2)
    return doc1.similarity(doc2)


if __name__ == "__main__":
    url1 = sys.argv[1]
    url2 = sys.argv[2]
    print('Downloading first article')
    article1, summary1 = get_text(url1)
    print('Downloading second article')
    article2, summary2 = get_text(url2)
    print('Finding similarity')
    low_similarity = get_similarity(article1, article2, accuracy="low")
    med_similarity = 0  # get_similarity(article1, article2, accuracy="medium")
    high_similarity = 0  # get_similarity(article1, article2, accuracy="high")
    print('Similarity: {} {} {}'.format(str(low_similarity), str(med_similarity), str(high_similarity)))
