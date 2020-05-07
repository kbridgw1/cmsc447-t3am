import json
from functools import partial
import pyproj
import geojson
import shapely
from shapely.geometry import MultiPolygon, asShape
from shapely.ops import unary_union, Polygon
from geojson import Point, Feature, FeatureCollection, dump


with open('swinggeo.json') as repgeo:
    geo = json.load(repgeo)

polys1 = []
polys2 = []
polys3 = []
polys4 = []
polys5 = []
polys6 = []
polys7 = []
polys8 = []

for feature in range(len(geo['features'])):
    poly = shapely.geometry.asShape(geo['features'][feature]['geometry'])
    x = geo['features'][feature]['properties']['CNG02']
    if x == 1:
        polys1.append(poly)
    elif x == 2:
        polys2.append(poly)
    elif x == 3:
        polys3.append(poly)
    elif x == 4:
        polys4.append(poly)
    elif x == 5:
        polys5.append(poly)
    elif x == 6:
        polys6.append(poly)
    elif x == 7:
        polys7.append(poly)
    elif x == 8:
        polys8.append(poly)

merge1 = unary_union(polys1)
merge2 = unary_union(polys2)
merge3 = unary_union(polys3)
merge4 = unary_union(polys4)
merge5 = unary_union(polys5)
merge6 = unary_union(polys6)
merge7 = unary_union(polys7)
merge8 = unary_union(polys8)

feats = []
merge1geo = geojson.Feature(geometry=merge1, properties={'cd':'1'})
feats.append(merge1geo)
merge2geo = geojson.Feature(geometry=merge2, properties={'cd':'2'})
feats.append(merge2geo)
merge3geo = geojson.Feature(geometry=merge3, properties={'cd':'3'})
feats.append(merge3geo)
merge4geo = geojson.Feature(geometry=merge4, properties={'cd':'4'})
feats.append(merge4geo)
merge5geo = geojson.Feature(geometry=merge5, properties={'cd':'5'})
feats.append(merge5geo)
merge6geo = geojson.Feature(geometry=merge6, properties={'cd':'6'})
feats.append(merge6geo)
merge7geo = geojson.Feature(geometry=merge7, properties={'cd':'7'})
feats.append(merge7geo)
merge8geo = geojson.Feature(geometry=merge8, properties={'cd':'8'})
feats.append(merge8geo)

feature_collection = FeatureCollection(feats)

with open('swingdistricts.json', 'w') as f:
   dump(feature_collection, f)