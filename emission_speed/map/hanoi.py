import osmnx as ox

# Tải mạng lưới đường phố của một thành phố (ví dụ: Hà Nội)
G = ox.graph_from_place('Hanoi, Vietnam', network_type='drive')

# Hiển thị mạng lưới đường phố
ox.plot_graph(G)
