import sys
import csv

import pycountry
from geopy import Point

from plot_circles import plot_circles
from circles import Circle


def read_circle_data(filename):
    circles = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            lat = float(row[3])
            lng = float(row[4])
            radius = float(row[5])
            center = Point(lat, lng)
            circle = Circle(center, radius)
            circles.append(circle)
    return circles


if __name__ == "__main__":
    filename = sys.argv[1]
    country_code = sys.argv[2]
    country_name = pycountry.countries.get(alpha_2=country_code).name
    print(country_name)
    circles = read_circle_data(filename)
    plot_circles(circles, country_name)
