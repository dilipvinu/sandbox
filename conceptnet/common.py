from json import JSONDecodeError
from time import sleep

import requests
from requests import ConnectionError, RequestException

BASE_URL = "http://34.239.143.232"  # "http://api.conceptnet.io"
MAX_RETRIES = 3


def get_uri_for_keyword(keyword, language="en"):
    url = "{}/uri?language={}&text={}".format(BASE_URL, language, keyword)
    try:
        res = get_response(url)
        return res["@id"]
    except RuntimeError:
        return keyword.lower().replace(" ", "_")


def get_keyword_for_uri(uri):
    # Get the last segment in uri (after last '/') and replace underscore with space
    return uri[uri.rfind("/") + 1:].replace("_", " ")


def get_response(url, retry=0):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError("Server error " + res.status_code)
        return res.json()
    except ConnectionError:
        if retry < MAX_RETRIES:
            print("Connection error, wait 5 seconds and retry")
            sleep(5)
            return get_response(url, retry + 1)
        raise RuntimeError("Connection error, aborting")
    except RequestException:
        raise RuntimeError("Request error")
    except JSONDecodeError:
        raise RuntimeError("Invalid JSON response")
