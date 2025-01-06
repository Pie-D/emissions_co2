# Export nodes to CSV
import osmnx as ox
import networkx as nx
import pandas as pd
from shapely.geometry import LineString
from emissions_co2.emission_speed.connection_mysql import *
import  numpy as np

# Tải dữ liệu mạng lưới đường bộ từ OpenStreetMap
place_name = "Montreal, Canada"
type_way = '["motorway", "trunk", "primary", "secondary"]'
custom_filter = '[highway~"motorway|trunk|primary|secondary"]'
# custom_filter = '[highway~"motorway|trunk|primary"]'
graph = ox.graph_from_place(
    place_name, network_type='drive', custom_filter=custom_filter)

# Chuyển đổi dữ liệu thành đồ thị
nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)
nodes.to_csv('montreal_nodes_v3.csv', index=True)

# Export edges to CSV
edges.to_csv('montreal_edges_v3.csv', index=True)

print("Data has been exported to CSV files successfully.")
