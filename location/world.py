import csv
import shapefile
from shapely.geometry import Polygon
from shapely.ops import cascaded_union



class AdmDiv:
    def __init__(self, country_id, state_id):
        self.country_id = country_id
        self.state_id = state_id

    def __eq__(self, other):
        return self.country_id == other.country_id and self.state_id == other.state_id


def combine_shapes(shapes):
    polygons = []
    for shape in shapes:
        polygons.append(Polygon(shape.points))
    combined = cascaded_union(polygons)


if __name__ == '__main__':
    sf = shapefile.Reader('/Users/dilip/Downloads/gadm28.shp/gadm28')
    fields = sf.fields[1:]
    field_names = [field[0] for field in fields]
    with open('out/adm1.csv', 'w') as file:
        writer = csv.DictWriter(file, field_names)
        writer.writeheader()
        index = 0
        attrs = None
        prev_adm = None
        adm_shapes = []
        for sr in sf.iterShapeRecords():
            attrs = dict(zip(field_names, sr.record))
            adm = AdmDiv(attrs['ID_0'], attrs['ID_1'])
            if prev_adm is not None and prev_adm != adm:
                writer.writerow(attrs)
                adm_shapes.append(sr.shape)
                index += 1
                break
            else:
                adm_shapes.append(sr.shape)
            prev_adm = adm
        writer.writerow(attrs)
        print(index, 'records found')
