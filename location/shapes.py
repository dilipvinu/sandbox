import sys

import pycountry
import shapefile
from geopy.distance import Point


def get_country_shape(country_code):
    sf = shapefile.Reader("/Users/dilip/Downloads/TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp")
    for index, record in enumerate(sf.records()):
        if record[1] == country_code:
            print('Record index', index)
            shape = sf.shape(index)
            print(len(shape.points), 'points in country shape')
            points = []
            for point in shape.points:
                points.append(Point(point[::-1]))
            return points


def get_state_shapes(country_code):
    code = pycountry.countries.get(alpha_2=country_code).alpha_3
    path = "/Users/dilip/Downloads/gadm/{}_adm_shp/{}_adm1.shp".format(code, code)
    sf = shapefile.Reader(path)
    fields = sf.fields[1:]
    field_names = [field[0] for field in fields]
    states = []
    for sr in sf.shapeRecords():
        attrs = dict(zip(field_names, sr.record))
        points = []
        for point in sr.shape.points:
            points.append(Point(point[::-1]))
        states.append({'name': attrs['NAME_1'], 'country': attrs['NAME_0'], 'type': attrs['ENGTYPE_1'],
                       'shape': points, 'bbox': sr.shape.bbox})
    return states


if __name__ == "__main__":
    country_code = sys.argv[1]
    get_country_shape(country_code)
