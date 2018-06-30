"""This example retrieves keywords that are related to a given keyword.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""
import sys
import time
import csv

from googleads import adwords
from suds import WebFault

PAGE_SIZE = 2


class SearchMode(object):
    LIST = "list"
    FLAT = "flat"


def get_keywords(client, mode, queries, exclusions=(), page_size=PAGE_SIZE):
    filtered_queries = list(filter(None, queries))
    keywords = []

    # Initialize appropriate service.
    targeting_idea_service = client.GetService(
        'TargetingIdeaService', version='v201708')

    search_parameters = [
        {
            'xsi_type': 'RelatedToQuerySearchParameter',
            'queries': list(filtered_queries) if mode == SearchMode.LIST else [' '.join(filtered_queries)]
            # 'queries': [' '.join(filtered_queries)]
        },
        {
            # Language setting (optional).
            # The ID can be found in the documentation:
            # https://developers.google.com/adwords/api/docs/appendix/languagecodes
            'xsi_type': 'LanguageSearchParameter',
            'languages': [{'id': '1000'}]
        },
        {
            # Network search parameter (optional)
            'xsi_type': 'NetworkSearchParameter',
            'networkSetting': {
                'targetGoogleSearch': True,
                'targetSearchNetwork': False,
                'targetContentNetwork': False,
                'targetPartnerSearchNetwork': False
            }
        }
    ]

    if len(exclusions) > 0:
        search_parameters.append(
            {
                'xsi_type': 'IdeaTextFilterSearchParameter',
                'excluded': exclusions
            }
        )

    locations = ['2056']  # ('2356', '2840')
    if len(locations) > 0:
        search_parameters.append(
            {
                # Location search parameter (optional)
                'xsi_type': 'LocationSearchParameter',
                'locations': [{'id': location} for location in locations]
            }
        )

    # Construct selector object and retrieve related keywords.
    offset = 0
    selector = {
        'searchParameters': search_parameters,
        'ideaType': 'KEYWORD',
        'requestType': 'IDEAS',
        'requestedAttributeTypes': ['KEYWORD_TEXT'], #'SEARCH_VOLUME', 'CATEGORY_PRODUCTS_AND_SERVICES'],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(page_size)
        }
    }
    more_pages = True
    while more_pages:
        keywords.extend(get_results(targeting_idea_service, selector))
        offset += page_size
        selector['paging']['startIndex'] = str(offset)
        # more_pages = offset < int(page['totalNumEntries'])
        more_pages = False
    return keywords


def get_results(targeting_idea_service, selector, retry=0):
    keywords = []
    try:
        page = targeting_idea_service.get(selector)

        # Display results.
        if 'entries' in page:
            for result in page['entries']:
                attributes = {}
                for attribute in result['data']:
                    attributes[attribute['key']] = getattr(attribute['value'], 'value', '0')
                # print('Keyword with "%s" text and average monthly search volume '
                #       '"%s" was found with Products and Services categories: %s.'
                #       % (attributes['KEYWORD_TEXT'],
                #          attributes['SEARCH_VOLUME'],
                #          attributes['CATEGORY_PRODUCTS_AND_SERVICES']))
                keywords.append(attributes['KEYWORD_TEXT'])
        else:
            print('No related keywords were found.')
    except WebFault as e:
        if retry < 3:
            for error in e.fault.detail.ApiExceptionFault.errors:
                if error['ApiError.Type'] == 'RateExceededError':
                    timeout = round(int(error['retryAfterSeconds']) * 1.25)
                    print("Rate limit exceeded, sleeping for {} seconds".format(timeout))
                    time.sleep(timeout)
                    return get_results(targeting_idea_service, selector, retry + 1)
        raise e
    return keywords


def get_related_keywords(classification, keyword, mode=SearchMode.FLAT):
    # Initialize client object.
    adwords_client = adwords.AdWordsClient.LoadFromStorage('googleads.yaml')
    related_keywords = set()

    print("\nLEVEL 1")
    print("=======")
    print(keyword)

    query = {classification, keyword}
    l2_keywords = get_keywords(adwords_client, mode, query)
    print("\nLEVEL 2")
    print("=======")
    for keyword in l2_keywords:
        print(keyword)

    l3_keywords = []
    for l2_keyword in l2_keywords:
        query = {classification, keyword, l2_keyword}
        l3_keywords.extend(get_keywords(adwords_client, mode, query, l3_keywords))
    print("\nLEVEL 3")
    print("=======")
    for keyword in l3_keywords:
        print(keyword)

    l4_keywords = []
    for l2_keyword in l2_keywords:
        for l3_keyword in l3_keywords:
            query = {keyword, l2_keyword, l3_keyword}
            l4_keywords.extend(get_keywords(adwords_client, mode, query, l4_keywords, 1))
    print("\nLEVEL 4")
    print("=======")
    for keyword in l4_keywords:
        print(keyword)
        related_keywords.add(keyword)

    print("\nKEYWORDS")
    print("========")
    print(related_keywords)
    return related_keywords


def evaluate_search_methods():
    with open('keyword_data.csv', 'r') as infile:
        reader = csv.reader(infile, delimiter=',', quotechar='"')
        next(reader, None)
        with open('keyword_data_out.csv', 'w') as outfile:
            writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Social Account', 'Keyword', 'Category', 'Comma Related Keywords',
                             'Space Related Keywords'])
            for row in reader:
                interest = row[1].strip()
                category = row[2].strip()
                print(interest, category)
                if category:
                    list_keywords = ','.join(get_related_keywords(category, interest, SearchMode.LIST))
                    flat_keywords = ','.join(get_related_keywords(category, interest, SearchMode.FLAT))
                    writer.writerow([row[0], row[1], row[2], list_keywords, flat_keywords])


if __name__ == '__main__':
    if len(sys.argv) > 2:
        classification = sys.argv[1]
        keyword = sys.argv[2]
        get_related_keywords(classification, keyword, SearchMode.FLAT)
    else:
        evaluate_search_methods()
