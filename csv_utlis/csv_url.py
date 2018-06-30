import sys
from urllib.request import urlopen
import csv
import codecs


def read_schema(url):
    response = urlopen(url)
    reader = csv.reader(codecs.iterdecode(response, 'utf-8'))
    count = 0
    for row in reader:
        values = tuple(row)
        print(values[0])
        count += 1
        if count > 1:
            break


if __name__ == "__main__":
    url = sys.argv[1]
    read_schema(url)
