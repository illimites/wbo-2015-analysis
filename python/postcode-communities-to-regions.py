from shapely.geometry import mapping, shape
from shapely.geometry.collection import GeometryCollection
from shapely.geometry import MultiPoint, MultiPolygon
import geojson
import pickle


with open('../data/processed/postcodes-gis.pkl','r') as fp:
    kody = pickle.load(fp)

kody2 = { unicode(k.replace('-','')) :  kody[k] for k in kody }

with open("./postcodes-communities-by-project-count.pkl","r") as fp:
    communities = pickle.load(fp)

clusters = { v : kody2[k] for k, v in communities.iteritems() if k in kody2[k] }

i = 0
for cl in clusters.values():
    poly = MultiPoint([stops[stops_array[x]] for x in cl]).convex_hull
    cluster_polygons.append(geojson.Feature(geometry=poly, id = i))
    i=i+1
 
feature_collection = geojson.FeatureCollection(cluster_polygons)

with open("postcodes-communities-by-project-count.geojson", 'w') as outfile:
    outfile.write(geojson.dumps(feature_collection))