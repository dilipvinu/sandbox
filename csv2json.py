import json
import sys
import csv


def parse_csv(input_file, column):
    with open(input_file, 'r') as file:
        reader = csv.reader(file, delimiter=',', quotechar='"')
        rows = list(reader)
    lines = []
    for row in rows:
        lines.append(row[column])
    return lines


def write_output(output_file, lines):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('{"reviews":[')
        file.write(','.join('"{}"'.format(line.replace('"', '\\"')) for line in lines))
        file.write(']}')

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 3:
        input_file = args[0]
        column = int(args[1])
        output_file = args[2]
        lines = parse_csv(input_file, column - 1)
        write_output(output_file, lines)
    else:
        print('Usage: csv2json.py input_file column_number output_file')
