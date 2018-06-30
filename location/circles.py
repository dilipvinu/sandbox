import os
import csv
import math
import sys

import pycountry
from country_bounding_boxes import country_subunits_by_iso_code
from geopy.distance import Point, VincentyDistance
from shapely.geometry import Polygon, box

sys.path.append(os.getcwd())
from shapes import get_state_shapes, get_country_shape

MIN_RADIUS = 25
MAX_RADIUS = 500


class Bounds:
    def __init__(self, bbox):
        self.bot_left = Point(bbox[1], bbox[0])
        self.top_right = Point(bbox[3], bbox[2])
        self.bot_right = Point(bbox[1], bbox[2])
        self.top_left = Point(bbox[3], bbox[0])
        self._width = get_distance(self.top_left, self.top_right)
        self._height = get_distance(self.top_left, self.bot_left)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def shape(self):
        points = [self.top_left, self.bot_left, self.bot_right, self.top_right]
        return points


class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def shape(self):
        points = []
        angle = 360
        while angle > 0:
            points.append(distance(self.radius).destination(point=self.center, bearing=angle))
            angle -= 1
        return points

    def bbox(self):
        box_radius = math.sqrt(2 * self.radius * self.radius)
        bot_left = distance(box_radius).destination(point=self.center, bearing=225)
        top_right = distance(box_radius).destination(point=self.center, bearing=45)
        return bot_left.longitude, bot_left.latitude, top_right.longitude, top_right.latitude


class PopulationCell:
    def __init__(self, density, bbox):
        self.bounds = Bounds(bbox)
        self.density = density


def get_distance(point1, point2):
    return VincentyDistance(point1, point2).kilometers


def get_hypotenuse(dist1, dist2):
    return math.sqrt(dist1 * dist1 + dist2 * dist2)


def distance(radius):
    return VincentyDistance(kilometers=radius)


def get_circles(bounds):
    radius = math.ceil(min(bounds.width(), bounds.height()) / 2)
    if radius < MIN_RADIUS:
        radius = MIN_RADIUS
    if radius > MAX_RADIUS:
        radius = MAX_RADIUS

    circles = []
    if bounds.height() / 2 > radius:
        start = bounds.bot_left
        prev_row_circles = []
        while True:
            start = distance(radius).destination(point=start, bearing=0)
            row_circles = get_horizontal_circles(radius, bounds, start)
            circles.extend(row_circles)
            filler_circles = get_filler_circles(prev_row_circles, row_circles, radius)
            circles.extend(filler_circles)
            prev_row_circles = row_circles
            if get_distance(start, bounds.top_left) < radius * 3:
                last_start = distance(radius).destination(point=bounds.top_left, bearing=180)
                if get_distance(start, last_start) > radius / 4:
                    last_row_circles = get_horizontal_circles(radius, bounds, last_start)
                    circles.extend(last_row_circles)
                    filler_circles = get_filler_circles(prev_row_circles, last_row_circles, radius)
                    circles.extend(filler_circles)
                break
            start = distance(radius).destination(point=start, bearing=0)
    else:
        start = distance(bounds.height() / 2).destination(point=bounds.bot_left, bearing=0)
        circles.extend(get_horizontal_circles(radius, bounds, start))
    return circles


def get_horizontal_circles(radius, bounds, start):
    circles = []
    center = Point(start.latitude, start.longitude)
    right = Point(start.latitude, bounds.bot_right.longitude)
    if bounds.width() / 2 > radius:
        while True:
            center = distance(radius).destination(point=center, bearing=90)
            circle = Circle(center, radius)
            circles.append(circle)
            if get_distance(center, right) < radius * 3:
                last_center = distance(radius).destination(point=right, bearing=270)
                last_circle = Circle(last_center, radius)
                if get_distance(circle.center, last_circle.center) > radius / 4:
                    circles.append(last_circle)
                break
            center = distance(radius).destination(point=center, bearing=90)
    else:
        center = distance(bounds.width() / 2).destination(point=center, bearing=90)
        circles.append(Circle(center, radius))
    return circles


def get_filler_circles(prev_row_circles, row_circles, radius):
    circles = []
    if len(prev_row_circles) < 2 or len(row_circles) < 2:
        return circles
    max_index = min(len(prev_row_circles), len(row_circles))
    index = 1
    while index < max_index:
        bottom = prev_row_circles[index - 1].center
        top = row_circles[index].center
        center = Point((bottom.latitude + top.latitude) / 2, (bottom.longitude + top.longitude) / 2)
        circles.append(Circle(center, radius / 2))
        index += 1
    return circles


def intersects(country_shape, circle):
    country_points = []
    for point in country_shape:
        country_points.append(tuple(point)[:2][::-1])
    circle_shape = circle.shape()
    circle_points = []
    for point in circle_shape:
        circle_points.append(tuple(point)[:2][::-1])
    country_polygon = Polygon(country_points)
    circle_polygon = Polygon(circle_points)
    # intersection_area = country_polygon.convex_hull.intersection(circle_polygon).area
    return country_polygon.intersects(circle_polygon)  # and intersection_area / circle_polygon.area > 0.2


def remove_contains(circles, index):
    popped_circle = circles.pop(index)
    popped_circle_box = box(*popped_circle.bbox())
    for circle in circles:
        circle_box = box(*circle.bbox())
        if circle_box.contains(popped_circle_box):
            return True
    circles.insert(index, popped_circle)
    return False


def load_population_map():
    grid = []
    with open('population_density.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        lat = 90
        for row in reader:
            lng = -180
            for value in row:
                if value != '99999.0':
                    density = float(value)
                    bbox = [lng, lat - 1, lng + 1, lat]
                    cell = PopulationCell(density, bbox)
                    grid.append(cell)
                lng += 1
            lat -= 1
    return grid


def circle_population_density(circle, population_grid):
    circle_shape = circle.shape()
    circle_points = []
    for point in circle_shape:
        circle_points.append(tuple(point)[:2][::-1])
    circle_polygon = Polygon(circle_points).convex_hull
    circle_cells = []
    for cell in population_grid:
        cell_shape = cell.bounds.shape()
        cell_points = []
        for point in cell_shape:
            cell_points.append(tuple(point)[:2][::-1])
        cell_polygon = Polygon(cell_points)
        if circle_polygon.intersects(cell_polygon):
            circle_cells.append(cell)
    if not circle_cells:
        return 0
    total_density = 0
    for cell in circle_cells:
        total_density += cell.density
    circle_density = total_density / len(circle_cells)
    return circle_density


def get_bounded_circles(shape, bounds):
    circles = []
    all_circles = get_circles(bounds)
    print('Checking for intersection')
    for circle in all_circles:
        if intersects(shape, circle):
            circles.append(circle)
    index = 0
    print('Removing redundant circles')
    while index < len(circles):
        if not remove_contains(circles, index):
            index += 1
    # return circles
    print('Removing sparsely populated circles')
    population_grid = load_population_map()
    dense_circles = []
    for circle in circles:
        if circle_population_density(circle, population_grid) > 1.1:
            dense_circles.append(circle)
    return dense_circles


def get_country_circles(country_code):
    subunits = country_subunits_by_iso_code(country_code)
    print('Getting shape for {}'.format(country_code))
    country_shape = get_country_shape(country_code)
    if country_shape is None:
        print('Country not found {}'.format(country_code))
    else:
        circles = []
        for unit in subunits:
            bounds = Bounds(unit.bbox)
            print(unit.name, bounds.width(), 'km,', bounds.height(), 'km')
            print('Finding circles for', unit.name)
            circles.extend(get_bounded_circles(country_shape, bounds))
        # points = circles[0].shape()
        # with open('out/points.csv', 'w') as file:
        #     writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #     for point in points:
        #         writer.writerow([point.latitude, point.longitude])
        return circles


def get_state_circles(country_code):
    states = get_state_shapes(country_code)
    circles = []
    for state in states:
        state_shape = state['shape']
        bounds = Bounds(state['bbox'])
        print(state['name'], bounds.width(), 'km,', bounds.height(), 'km')
        print('Finding circles for', state['name'])
        state_circles = get_bounded_circles(state_shape, bounds)
        for circle in state_circles:
            circles.append({
                'name': state['name'],
                'country': state['country'],
                'code': country_code,
                'type': state['type'],
                'circle': circle
            })
    return circles


def get_supported_country(ad_countries, country_code):
    for ad_country in ad_countries:
        if ad_country['code'] == country_code:
            return ad_country


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'country':
            countries = list(pycountry.countries)
            ad_countries = []
            with open('adwords_countries.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                rows = list(reader)
                for row in rows[1:]:
                    ad_countries.append({'code': row[4], 'name': row[1]})
            with open('out/circles_filtered.csv', 'w') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Country", "Code", "Numeric Code", "Latitude", "Longitude", "Radius"])
                for country in countries:
                    ad_country = get_supported_country(ad_countries, country.alpha_2)
                    if ad_country is not None and country.alpha_2 != 'AQ':
                        circles = get_country_circles(country.alpha_2)
                        if circles is not None:
                            for circle in circles:
                                print(tuple(circle.center)[:2], circle.radius)
                                writer.writerow([ad_country['name'], country.alpha_2, country.numeric,
                                                 circle.center.latitude, circle.center.longitude,
                                                 circle.radius])
                            print(len(circles), 'circles')
        elif sys.argv[1] == 'state':
            country_code = sys.argv[2]
            circles = get_state_circles(country_code)
            with open('out/circles_' + country_code + '_states.csv', 'w') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Name", "Type", "Country", "Code", "Latitude", "Longitude", "Radius"])
                for circle in circles:
                    print(tuple(circle['circle'].center)[:2], circle['circle'].radius)
                    writer.writerow([circle['name'], circle['type'], circle['country'], circle['code'],
                                     circle['circle'].center.latitude, circle['circle'].center.longitude,
                                     circle['circle'].radius])
                print(len(circles), 'circles')
        else:
            country_code = sys.argv[1]
            country = pycountry.countries.get(alpha_2=country_code)
            circles = get_country_circles(country.alpha_2)
            if circles is not None:
                with open('out/circles_' + country_code + '.csv', 'w') as csv_file:
                    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(["Country", "Code", "Numeric Code", "Latitude", "Longitude", "Radius"])
                    for circle in circles:
                        print(tuple(circle.center)[:2], circle.radius)
                        writer.writerow([country.name, country.alpha_2, country.numeric,
                                         circle.center.latitude, circle.center.longitude,
                                         circle.radius])
                    print(len(circles), 'circles')
