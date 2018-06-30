import csv

import requests
import time

from conceptnet.common import BASE_URL, get_keyword_for_uri, get_uri_for_keyword, get_response

NOUN_RELATIONS = ("RelatedTo", "IsA", "PartOf", "HasA", "Synonym", "DerivedFrom", "DefinedAs", "SimilarTo")
VERB_RELATIONS = ("UsedFor", "CapableOf", "Causes", "MannerOf", "ReceivesAction")
ADJECTIVE_RELATIONS = ("HasProperty", "SymbolOf", "MadeOf")


# def get_related_words(keyword, category, language="en"):
#     related_words = []
#     node_uri = get_uri_for_keyword(keyword, language=language)
#     category_uri = get_uri_for_keyword(category, language=language)
#     node_category_relations = get_relations(node_uri, category_uri)
#     url = "{}/related{}?filter=/c/{}".format(BASE_URL, node_uri, language)
#     res = requests.get(url).json()
#     for related_node in res["related"]:
#         related_node_uri = related_node["@id"]
#         related_word = get_keyword_for_uri(related_node_uri)
#         if related_word.lower() == keyword.lower():
#             continue
#         relations = get_relations(node_uri, related_node_uri)
#         if not has_valid_relations(relations):
#             continue
#         related_node_category_relations = get_relations(related_node_uri, category_uri)
#         if not has_common_relations(node_category_relations, related_node_category_relations):
#             continue
#         related_words.append(related_word)
#     return related_words


def get_related_words(keyword, category, relation_set, language="en"):
    related_words = []
    related_categories = []
    for relation in relation_set:
        words_with_relation = get_words_with_relation(keyword, relation, language)
        related_words.extend(words_with_relation)
        categories_with_relation = get_words_with_relation(category, relation, language)
        related_categories.extend(categories_with_relation)
    keyword_uri = get_uri_for_keyword(keyword, language)
    for related_category in related_categories:
        related_category_uri = get_uri_for_keyword(related_category, language)
        relations = get_relations(keyword_uri, related_category_uri)
        for relation in relations:
            if relation["weight"] > 0.5:
                related_words.append(related_category)
                break
    return related_words


def get_words_with_relation(keyword, relation="RelatedTo", language="en"):
    print("Getting words with relation {} for {}".format(relation, keyword))
    node_uri = get_uri_for_keyword(keyword, language=language)
    edges = query(node_uri, relation)
    related_words = []
    for edge in edges:
        start = edge["start"]
        end = edge["end"]
        if start["@id"] == node_uri or start["term"] == node_uri:
            other = end
        else:
            other = start
        if other["language"] != language:
            continue
        if edge["weight"] < 0.5:
            continue
        related_words.append(other["label"])
    print("{} results".format(len(related_words)))
    return related_words


def query(node, rel):
    url = "{}/query?node={}&rel=/r/{}&limit=1000".format(BASE_URL, node, rel)
    edges = []
    has_more = True
    while has_more:
        try:
            res = get_response(url)
            edges.extend(res["edges"])
            view = res.get("view", {})
            next_page = view.get("nextPage", "")
            if next_page:
                url = "{}/{}".format(BASE_URL, next_page)
            else:
                has_more = False
        except RuntimeError:
            break
    return edges


def get_relations(node_uri, related_node_uri):
    print("Getting relations between {} and {}".format(get_keyword_for_uri(node_uri),
                                                       get_keyword_for_uri(related_node_uri)))
    url = "{}/query?node={}&other={}".format(BASE_URL, node_uri, related_node_uri)
    relations = []
    try:
        res = get_response(url)
        for edge in res["edges"]:
            relations.append({"rel": edge["rel"], "weight": edge["weight"]})
    except RuntimeError:
        pass
    print("{} relations".format(len(relations)))
    return relations


def has_valid_relations(relations, valid_relation_types=()):
    # if not relations:
    #     return False
    if not valid_relation_types:
        return True
    for relation in relations:
        if relation["label"] in valid_relation_types:
            return True
    return False


def has_common_relations(relations, other_relations):
    relation_types = set([relation["label"] for relation in relations])
    other_relation_types = set([other_relation["label"] for other_relation in other_relations])
    return bool(relation_types & other_relation_types)


def compare_interests(filename):
    with open(filename, 'r') as in_file, open('related_words.csv', 'w') as out_file:
        csv_reader = csv.reader(in_file, delimiter=',', quotechar='"')
        next(csv_reader)
        csv_writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Interest', 'Category', 'Datamuse Nouns', 'Datamuse Verbs', 'Datamuse Adjectives',
                             'ConceptNet Nouns', 'ConceptNet Verbs', 'ConceptNet Adjectives'])
        for row in csv_reader:
            keyword = row[0]
            category = row[1]
            d_nouns = row[2]
            d_verbs = row[3]
            d_adjectives = row[4]
            # print("Wait 10 seconds")
            # time.sleep(10)
            c_nouns = ",".join(get_related_words(keyword, category, NOUN_RELATIONS))
            # print("Wait 10 seconds")
            # time.sleep(10)
            c_verbs = ",".join(get_related_words(keyword, category, VERB_RELATIONS))
            # print("Wait 10 seconds")
            # time.sleep(10)
            c_adjectives = ",".join(get_related_words(keyword, category, ADJECTIVE_RELATIONS))
            csv_writer.writerow([keyword, category, d_nouns, d_verbs, d_adjectives, c_nouns, c_verbs, c_adjectives])


if __name__ == "__main__":
    # keyword = sys.argv[1]
    # category = sys.argv[2]
    # related_keywords = get_related_words(keyword, category)
    # print(related_keywords)
    compare_interests('interests.csv')
