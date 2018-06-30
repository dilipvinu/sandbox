import csv


def get_calendars():
    calendars = []
    with open("google_calendars.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for row in reader:
            calendar = {
                "name": row[0],
                "code": row[1].split('#')[0].split('.')[1]
            }
            calendars.append(calendar)
    return calendars


if __name__ == "__main__":
    calendars = get_calendars()
    for calendar in calendars:
        print(calendar)
