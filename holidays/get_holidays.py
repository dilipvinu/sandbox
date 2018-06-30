import requests
from requests import RequestException

from get_calendars import get_calendars

import csv


def get_holidays(calendar_code):
    url = "https://www.googleapis.com/holidays/v3/calendars/{}__en%40holiday.holidays.google.com/events?" \
          "key=AIzaSyAZzxl_xXUSbQDN0x-IPg4kt8bVDQwLZUI".format(calendar_code)
    try:
        response = requests.get(url)
        if 200 <= response.status_code < 300:
            return parse_response(response.json())
        else:
            return []
    except RequestException:
        return []


def get_all_holidays():
    with open("holidays.csv", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Country", "Holiday", "Start Date", "End Date"])
        calendars = get_calendars()
        for calendar in calendars:
            print("Getting {}".format(calendar["name"]))
            holidays = get_holidays(calendar["code"])
            for holiday in holidays:
                writer.writerow([calendar["name"], holiday["name"], holiday["start"], holiday["end"]])


def parse_response(response):
    holidays = []
    if "items" in response:
        for item in response["items"]:
            holiday = {
                "name": item["summary"],
                "start": item["start"]["date"],
                "end": item["end"]["date"]
            }
            holidays.append(holiday)
    return holidays


if __name__ == "__main__":
    get_all_holidays()
