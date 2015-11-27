from graph_tool.all import *
import pickle
import pandas as pd


from shapely.geometry import mapping, shape
from shapely.geometry.collection import GeometryCollection
from shapely.geometry import MultiPoint, MultiPolygon


with open("./postcodes-coocuring-weights.pkl","r") as fp:
    dane = pickle.load(fp)


graf = dane['codes_weighted_by_project_count']

ug = Graph(directed=False)
edge_weights = ug.new_edge_property('int64_t')

vertex_dict = {}
for c in graf.keys():
	vertex_dict[c] = ug.add_vertex()

edges = []
for k1 in graf.keys():
    for k2 in graf[k1].keys():
        if int(k2) > int(k1) and graf[k1][k2] > 0:
            edges.append([k1, k2, graf[k1][k2]])

for vec in edges:
    v1 = vertex_dict[vec[0]]
    v2 = vertex_dict[vec[1]]
    e = ug.add_edge(v1, v2)
    edge_weights[e] = vec[2]

state = minimize_blockmodel_dl(ug, eweight = edge_weights)
blocks = state.get_blocks()

communities = {}

for postcode, vertex in vertex_dict.iteritems():
	communities[postcode] = blocks[vertex]

with open("./postcodes-communities-by-project-count.pkl","w") as fp:
    pickle.dump(communities, fp)
