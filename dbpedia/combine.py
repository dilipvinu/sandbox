import sys
import csv


def combine_rows(filename):
    values = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
        for row in rows[1:]:
            values.append(row[1])
    return ','.join(values)


def combine_data(member_file, alt_name_file, affiliation_file, custom_file, combined_file):
    members = combine_rows(member_file)
    alt_names = combine_rows(alt_name_file)
    affiliations = combine_rows(affiliation_file)
    custom = combine_rows(custom_file)
    with open(combined_file, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['members', 'alternate names', 'affiliations', 'custom'])
        writer.writerow([members, alt_names, affiliations, custom])


if __name__ == "__main__":
    member_file = sys.argv[1]
    alt_name_file = sys.argv[2]
    affiliation_file = sys.argv[3]
    custom_file = sys.argv[4]
    combined_file = sys.argv[5]
    combine_data(member_file, alt_name_file, affiliation_file, custom_file, combined_file)
