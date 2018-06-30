import unicodedata
from SPARQLWrapper import SPARQLWrapper, JSON


def get_party_members(sparql):
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?name ?label
        WHERE {
            ?name rdfs:label ?label .
            ?name dbo:party dbr:Indian_National_Congress .
            FILTER langMatches(lang(?label),'en')
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print_results(results)


def get_alternate_names(sparql):
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?name ?label
        WHERE {
            ?name rdfs:label ?label .
            ?name dbo:wikiPageDisambiguates dbr:Indian_National_Congress .
            FILTER langMatches(lang(?label),'en')
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print_results(results)


def get_affiliations(sparql):
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?name ?label
        WHERE {
            ?name dbp:alliance dbr:United_Progressive_Alliance .
            MINUS {
                ?name dbp:alliance <http://dbpedia.org/resource/National_Democratic_Alliance_(India)>
            } .
            ?name rdfs:label ?label .
            FILTER langMatches(lang(?label),'en')
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print_results(results)


def print_results(results):
    for binding in results['results']['bindings']:
        value = binding['label']['value']
        try:
            print(normalize(value))
        except UnicodeError as e:
            print(e)
            break


def normalize(string):
    return ''.join((c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn'))


if __name__ == "__main__":
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    print('PARTY MEMBERS')
    get_party_members(sparql)

    print('ALTERNATE_NAMES')
    get_alternate_names(sparql)

    print('PARTY AFFILIATIONS')
    get_affiliations(sparql)
