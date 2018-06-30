import json
import csv


if __name__ == '__main__':
    categories = set()
    with open('facebook_categories.json', 'r') as file:
        data = json.loads(file.read())['data']
        for category in data:
            if len(category['path']) == 2 or len(category['name'].split()) < 3:
                categories.add((category['id'], category['name'], category['path'][0]))

    with open('categories.csv', 'w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Targeting ID', 'Name', 'Parent'])
        for category in categories:
            writer.writerow(category)
