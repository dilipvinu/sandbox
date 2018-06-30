import argparse
import csv


def read_file(file_name):
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        return list(reader)


def combine_files(input_files, output_file):
    with open(output_file, 'w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for input_file in input_files:
            rows = read_file(input_file)
            for row in rows[1:]:
                writer.writerow(row)


parser = argparse.ArgumentParser(description='Combine csv files')
parser.add_argument('inputs', metavar='input', type=str, nargs='+', help='input file(s)')
parser.add_argument('--output', help='output file', required=True)

args = parser.parse_args()
combine_files(args.inputs, args.output)
