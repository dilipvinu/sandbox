from requests import RequestException

import csv
import requests


def run_query(url):
    posts = []
    more_results = 0
    next_url = ''
    try:
        response = requests.get(url).json()
        posts = response['posts']
        more_results = response['moreResultsAvailable']
        next_url = response['next']
    except RequestException as e:
        print(e)
    return posts, more_results, next_url


def get_data():
    url = 'http://webhose.io/filterWebContent?token=128f5c9f-da10-4042-8128-e510e083f2c1&format=json&ts=1521777552731&sort=crawled&q=(%22pinarayi%20vijayan%22%20OR%20%22%E0%B4%AA%E0%B4%BF%E0%B4%A3%E0%B4%B1%E0%B4%BE%E0%B4%AF%E0%B4%BF%20%E0%B4%B5%E0%B4%BF%E0%B4%9C%E0%B4%AF%E0%B5%BB%22%20OR%20%23pinarayivijayan)'
    more_available = True
    with open('pinarayi_webhose.csv', 'w', encoding='utf-8') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        while more_available:
            print('Fetching next page')
            posts, more_results, next_url = run_query(url)
            for post in posts:
                writer.writerow([post['uuid'], post['published'], post['thread']['site_full'], post['url'],
                                 post['author'], post['title'], post['text'], post['language']])
            more_available = more_results > 0
            url = 'http://webhose.io{}'.format(next_url)


if __name__ == '__main__':
    get_data()
