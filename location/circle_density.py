import csv

import gmplot
from circles import Bounds


class PopulationCell:
    def __init__(self, density, bbox):
        self.bounds = Bounds(bbox)
        self.density = density


def load_population_map():
    grid = []
    with open('population_density.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        lat = 90
        for row in reader:
            lng = -180
            for value in row:
                if value != '99999.0' and value != '1.04':
                    print(value)
                    density = float(value)
                    bbox = [lng, lat - 1, lng + 1, lat]
                    cell = PopulationCell(density, bbox)
                    grid.append(cell)
                lng += 1
            lat -= 1
    return grid


def get_lat_long(circle):
    points = circle.bounds.shape()
    latitudes = []
    longitudes = []
    for point in points:
        latitudes.append(point.latitude)
        longitudes.append(point.longitude)
    return latitudes, longitudes


def plot_grid(grid, country_name):
    gmap = gmplot.GoogleMapPlotter.from_geocode(country_name, zoom=4)
    for cell in grid:
        latitudes, longitudes = get_lat_long(cell)
        gmap.plot(latitudes, longitudes, 'cornflowerblue', edge_width=2)
    gmap.draw(country_name + ".html")


if __name__ == "__main__":
    grid = load_population_map()
    plot_grid(grid, 'India')
