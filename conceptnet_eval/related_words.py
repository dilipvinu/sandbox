import csv

from conceptnet5.db.query import AssertionFinder

from conceptnet_eval.common import BASE_URL, get_keyword_for_uri, get_response, get_uri_for_keyword

NOUN_RELATIONS = ("RelatedTo", "IsA", "PartOf", "HasA", "Synonym", "DerivedFrom", "DefinedAs", "SimilarTo")
VERB_RELATIONS = ("UsedFor", "CapableOf", "Causes", "MannerOf", "ReceivesAction")
ADJECTIVE_RELATIONS = ("HasProperty", "SymbolOf", "MadeOf")
ALL_RELATIONS = ("RelatedTo", "FormOf", "IsA", "PartOf", "HasA", "UsedFor", "CapableOf", "AtLocation",
                 "Causes", "HasSubevent", "HasFirstSubevent", "HasLastSubevent", "HasPrerequisite", "HasProperty",
                 "MotivatedByGoal", "ObstructedBy", "Desires", "CreatedBy", "Synonym", "Antonym", "DistinctFrom",
                 "DerivedFrom", "SymbolOf", "DefinedAs", "Entails", "MannerOf", "LocatedNear", "HasContext",
                 "SimilarTo", "EtymologicallyRelatedTo", "EtymologicallyDerivedFrom", "CausesDesire", "MadeOf",
                 "ReceivesAction", "InstanceOf", "dbpedia/genre", "dbpedia/influencedBy", "dbpedia/knownFor",
                 "dbpedia/occupation", "dbpedia/language", "dbpedia/field", "dbpedia/product", "dbpedia/capital",
                 "dbpedia/leader")

RUN_MODE = "remote"


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
    mode = RUN_MODE
    related_words = set()
    related_categories = set()
    keyword_uri = get_uri_for_keyword(keyword, language=language, mode=mode)
    category_uri = get_uri_for_keyword(category, language=language, mode=mode)
    for relation in relation_set:
        words_with_relation = get_words_with_relation(keyword_uri, relation, language, mode)
        related_words.update(words_with_relation)
        categories_with_relation = get_words_with_relation(category_uri, relation, language, mode)
        related_categories.update(categories_with_relation)
    related_words_with_weight = get_related_words_with_weight(category_uri, related_words, language, mode)
    related_categories_with_weight = get_related_words_with_weight(keyword_uri, related_categories, language, mode)
    return related_words_with_weight, related_categories_with_weight


def get_related_words_with_weight(keyword_uri, related_words, language="en", mode="remote"):
    related_words_with_weight = []
    for related_word in related_words:
        related_word_uri = get_uri_for_keyword(related_word, language=language, mode=mode)
        max_relation = get_max_relation(related_word_uri, keyword_uri, mode)
        if max_relation:
            related_words_with_weight.append((related_word, max_relation["weight"]))
    return related_words_with_weight


def get_max_relation(node_uri, other_uri, mode):
    max_relation = {"weight": 0.0}
    relations = get_relations(node_uri, other_uri, mode)
    for relation in relations:
        if relation["weight"] > max_relation["weight"]:
            max_relation = relation
    if max_relation["weight"] > 0.0:
        return max_relation


def get_words_with_relation(keyword_uri, relation="RelatedTo", language="en", mode="remote"):
    print("Getting words with relation {} for {}".format(relation, get_keyword_for_uri(keyword_uri)))
    edges = get_related(keyword_uri, relation, mode)
    related_words = []
    for edge in edges:
        start = edge["start"]
        end = edge["end"]
        if start["@id"] == keyword_uri or start["term"] == keyword_uri:
            other = end
        else:
            other = start
        if other["language"] != language:
            continue
        related_words.append(other["label"])
    print("{} results".format(len(related_words)))
    return related_words


def get_related(node_uri, rel, mode):
    params = {
        "node": node_uri,
        "rel": "/r/{}".format(rel)
    }
    return query(params, mode=mode)


def get_relations(node_uri, related_node_uri, mode):
    print("Getting relations between {} and {}".format(get_keyword_for_uri(node_uri),
                                                       get_keyword_for_uri(related_node_uri)))
    params = {
        "node": node_uri,
        "other": related_node_uri
    }
    edges = query(params, mode=mode)
    relations = []
    for edge in edges:
        relations.append({"rel": edge["rel"], "weight": edge["weight"]})
    print("{} relations".format(len(relations)))
    return relations


def query(params, limit=1000, mode="remote"):
    all_edges = []
    if mode == "remote":
        url = "{}/query?limit={}".format(BASE_URL, limit)
        for key, value in params.items():
            url += "&{}={}".format(key, value)
        while True:
            try:
                res = get_response(url)
                edges = res.get("edges", [])
                if not edges:
                    break
                all_edges.extend(edges)
                view = res.get("view", {})
                next_page = view.get("nextPage", "")
                if not next_page:
                    break
                url = "{}/{}".format(BASE_URL, next_page)
            except RuntimeError:
                break
    else:
        finder = AssertionFinder()
        offset = 0
        while True:
            edges = finder.query(params, limit=limit, offset=offset)
            if not edges:
                break
            all_edges.extend(edges)
            offset += limit
    return all_edges


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


def get_cross_relations(keywords, other_keywords, language="en", mode="remote"):
    cross_relations = []
    for keyword in keywords:
        for other_keyword in other_keywords:
            keyword_uri = get_uri_for_keyword(keyword, language=language, mode=mode)
            other_keyword_uri = get_uri_for_keyword(other_keyword, language=language, mode=mode)
            max_relation = get_max_relation(keyword_uri, other_keyword_uri, mode)
            if max_relation:
                cross_relations.append((keyword, other_keyword, max_relation["weight"]))
    return cross_relations


def to_str(tuple_list):
    flat_list = ["{} ({})".format(item[0], item[1]) for item in tuple_list]
    return ", ".join(flat_list)


def to_str_2(tuple_list):
    flat_list = ["{} - {} ({})".format(item[0], item[1], item[2]) for item in tuple_list]
    return ", ".join(flat_list)


def compare_interests(filename):
    with open(filename, 'r') as in_file, open('related_words.csv', 'w') as out_file:
        csv_reader = csv.reader(in_file, delimiter=',', quotechar='"')
        next(csv_reader)
        csv_writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Interest', 'Category', 'Datamuse Nouns', 'Datamuse Verbs', 'Datamuse Adjectives',
                             # 'CN Keyword Nouns', 'CN Category Nouns', 'CN Keyword Verbs', 'CN Category Verbs',
                             # 'CN Keyword Adjectives', 'CN Category Adjectives',
                             'CN Related Keywords', 'CN Related Categories', 'CN Cross Relations'])
        row_count = 0
        for row in csv_reader:
            keyword = row[0]
            category = row[1]
            d_nouns = row[2]
            d_verbs = row[3]
            d_adjectives = row[4]
            # ck_nouns, cc_nouns = get_related_words(keyword, category, NOUN_RELATIONS)
            # ck_verbs, cc_verbs = get_related_words(keyword, category, VERB_RELATIONS)
            # ck_adjectives, cc_adjectives = get_related_words(keyword, category, ADJECTIVE_RELATIONS)
            cn_keywords, cn_categories = get_related_words(keyword, category, ALL_RELATIONS)
            cnk = [keyword[0] for keyword in cn_keywords]
            cnc = [category[0] for category in cn_categories]
            cn_crosswords = get_cross_relations(cnk, cnc, mode=RUN_MODE)

            csv_writer.writerow([keyword, category, d_nouns, d_verbs, d_adjectives,
                                 # to_str(ck_nouns), to_str(cc_nouns), to_str(ck_verbs), to_str(cc_verbs),
                                 # to_str(ck_adjectives), to_str(cc_adjectives),
                                 to_str(cn_keywords), to_str(cn_categories), to_str_2(cn_crosswords)])
            row_count += 1
            if row_count == 10:
                break


if __name__ == "__main__":
    # keyword = sys.argv[1]
    # category = sys.argv[2]
    # related_keywords = get_related_words(keyword, category)
    # print(related_keywords)
    compare_interests('interests.csv')
