import sys

import gmplot
import pycountry

from circles import get_country_circles, get_bounded_circles, Bounds
from shapes import get_state_shapes


def get_lat_long(circle):
    points = circle.shape()
    latitudes = []
    longitudes = []
    for point in points:
        latitudes.append(point.latitude)
        longitudes.append(point.longitude)
    return latitudes, longitudes


def plot_circles(circles, country_name):
    gmap = gmplot.GoogleMapPlotter.from_geocode(country_name, zoom=4)
    for circle in circles:
        latitudes, longitudes = get_lat_long(circle)
        gmap.plot(latitudes, longitudes, 'cornflowerblue', edge_width=2)
    gmap.draw(country_name + ".html")


if __name__ == "__main__":
    country_code = sys.argv[1]
    country_name = pycountry.countries.get(alpha_2=country_code).name
    if len(sys.argv) == 2:
        circles = get_country_circles(country_code)
    else:
        state = sys.argv[2]
        circles = []
        states = get_state_shapes(country_code)
        for state in states:
            if state['name'] == state:
                state_shape = state['shape']
                bounds = Bounds(state['bbox'])
                state_circles = get_bounded_circles(state_shape, bounds)
                for circle in state_circles:
                    circles.append(circle)
                break
    if circles is not None:
        plot_circles(circles, country_name)
