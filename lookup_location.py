"""This example gets all LocationCriterion.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""
import sys
import csv

from googleads import adwords


def get_location_string(location):
    return '%s (%s)' % (location['locationName'], location['displayType']
    if 'displayType' in location else None)


def get_parent_country(location_criterion):
    if 'parentLocations' in location_criterion['location'] and location_criterion['location']['parentLocations']:
        for parent in location_criterion['location']['parentLocations']:
            if parent['displayType'] == 'Country':
                return parent


def is_state(location_criterion):
    if 'parentLocations' in location_criterion['location'] and location_criterion['location']['parentLocations']:
        if len(location_criterion['location']['parentLocations']) == 1 and \
                        location_criterion['location']['parentLocations'][0]['displayType'] == 'Country':
            return True
    return False


def get_locations(client, location_names):
    # Initialize appropriate service.
    location_criterion_service = client.GetService(
        'LocationCriterionService', version='v201708')

    # location_names = ['Paris', 'Quebec', 'Spain', 'Deutchland']

    # Create the selector.
    selector = {
        'fields': ['Id', 'LocationName', 'DisplayType', 'CanonicalName',
                   'ParentLocations', 'Reach', 'TargetingStatus'],
        'predicates': [{
            'field': 'LocationName',
            'operator': 'IN',
            'values': location_names
        }, {
            'field': 'Locale',
            'operator': 'EQUALS',
            'values': ['en']
        }]
    }

    # Make the get request.
    location_criteria = location_criterion_service.get(selector)

    locations = []
    index = 0
    # Display the resulting location criteria.
    for location_criterion in location_criteria:
        parent_string = ''
        if ('parentLocations' in location_criterion['location']
            and location_criterion['location']['parentLocations']):
            parent_string = ', '.join([get_location_string(parent) for parent in
                                       location_criterion['location']
                                       ['parentLocations']])
        # if location_criterion['location']['displayType'] != 'Country':
        #     continue
        if location_criterion['location']['locationName'] not in location_names:
            continue
        if not is_state(location_criterion):
            continue
        # print('The search term "%s" returned the location "%s" of type "%s"'
        #       ' with parent locations "%s", reach "%s" and id "%s" (%s)'
        #       % (location_criterion['searchTerm'],
        #          location_criterion['location']['locationName'],
        #          location_criterion['location']['displayType'], parent_string,
        #          location_criterion['reach']
        #          if 'reach' in location_criterion else None,
        #          location_criterion['location']['id'],
        #          location_criterion['location']['targetingStatus']))
        parent = get_parent_country(location_criterion)
        print(location_criterion['location']['id'], location_criterion['location']['locationName'],
              parent['locationName'] if parent is not None else '')
        locations.append((location_criterion['location']['id'], location_criterion['location']['locationName'],
                          parent['locationName']))
        index += 1
    print(index, "locations")
    return locations


if __name__ == '__main__':
    # Initialize client object.
    adwords_client = adwords.AdWordsClient.LoadFromStorage('googleads.yaml')

    location_names = []
    filename = sys.argv[1]
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            location_names.append(row)
    location_ids = set()
    with open('state_codes.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for location in location_names:
            rows = get_locations(adwords_client, [location[0]])
            if len(rows) > 0:
                for row in rows:
                    if not row[0] in location_ids:
                        writer.writerow([location[0], location[1], row[0], row[1], row[2]])
                        location_ids.add(row[0])
            else:
                writer.writerow([location[0], location[1], '', '', ''])
