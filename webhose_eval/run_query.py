import argparse
import urllib.parse

import csv
import requests


def run_query(queries, output_filename):
    quoted_queries = ['"{}"'.format(query) for query in queries]
    q = '({})'.format(' OR '.join(quoted_queries))
    print(urllib.parse.urlencode(q))
    print(output_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run query on WebHose')
    parser.add_argument('queries', metavar='query', type=str, nargs='+', help='queries to run')
    parser.add_argument('--output', help='output file', required=True)
    args = parser.parse_args()
    run_query(args.queries, args.output)
