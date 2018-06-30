import sys
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from requests import RequestException


def get_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
        return requests.get(url, headers=headers).text
    except RequestException as e:
        print("Request exception", e)


def get_search_url(product_name):
    encoded_product_name = quote(product_name)
    return "https://www.emag.ro/search/{}".format(encoded_product_name)


def get_search_result_links(product_name):
    search_url = get_search_url(product_name)
    links = []
    content = get_content(search_url)
    if not content:
        return
    soup = BeautifulSoup(content, 'html.parser')
    card_grid = soup.find(id="card_grid")
    if not card_grid:
        print("Card grid not found")
        return
    tags = card_grid.find_all("h2", {"class": "card-body product-title-zone"})
    for tag in tags:
        links.append(tag.a["href"])
    return links


if __name__ == "__main__":
    product_name = sys.argv[1]
    links = get_search_result_links(product_name)
    if not links:
        print("No results")
    else:
        for link in links:
            print(link)
        print("Total", len(links), "results")
