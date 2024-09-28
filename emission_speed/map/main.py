import osmnx as ox
import networkx as nx
import pandas as pd
from shapely.geometry import LineString
from connection_mysql import *
# Tải dữ liệu mạng lưới đường bộ từ OpenStreetMap
place_name = "Montreal, Canada"
type_way = '["motorway", "trunk", "primary", "secondary"]'
# custom_filter = '[highway~"motorway|trunk|primary|secondary"]'
custom_filter = '[highway~"motorway|trunk|primary|secondary"]'
graph = ox.graph_from_place(
    place_name, network_type='drive', custom_filter=custom_filter)

# Chuyển đổi dữ liệu thành đồ thị
nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)
conn, cursor = connect_db()
print(nodes.head())
print(edges.head())
# Nhập bảng nodes vào SQL
nodes_df = pd.DataFrame({
    'ID_P': nodes.index,
    'Longitude': nodes['x'],  # Kinh độ
    'Latitude': nodes['y']  # Vĩ độ
})

print("Index before reset_index:", edges.index)

# Chuyển đổi MultiIndex thành các cột riêng biệt
edges = edges.reset_index()

# Kiểm tra các cột của edges sau khi reset_index
print("Columns after reset_index:", edges.columns)

# Nếu u và v không có trong cột, kiểm tra chỉ số
print("Index after reset_index:", edges.index)
# Kiểm tra kết quả
# print(nodes_df.head())
# insert_node_into_database(conn, cursor, nodes_df)
# Nhập bảng edges vào SQL
edges_df = pd.DataFrame({
    'ID_E': edges['osmid'],
    'Name_E': edges['name'],  # Tên đường
    # Điểm đầu
    'F_PointID': edges['u'],
    # Điểm cuối
    'T_PointID': edges['v'],
    'Length': edges['length'],  # Chiều dài đường
    # Đường một chiều (0) hay hai chiều (1)
    'Two_way': edges['oneway'].apply(lambda x: 0 if x else 1),
    'Lane_number': edges['lanes']  # Số làn đường
})
edges_df['Name_E'] = edges_df['Name_E'].fillna('')
edges_df['F_PointID'] = edges_df['F_PointID'].fillna(0)
edges_df['T_PointID'] = edges_df['T_PointID'].fillna(0)
mean_length = edges_df['Length'].mean()
edges_df['Length'] = edges_df['Length'].fillna(mean_length)
edges_df['Two_way'] = edges_df['Two_way'].fillna(0)
edges_df['Lane_number'] = edges_df['Lane_number'].fillna(1)
with open('output.txt', 'a', encoding='utf-8') as file:
    # Ghi thêm nội dung
    for _, edge in edges_df.iterrows():
        file.write(
            # f"{edge['ID_E']} --- {edge['ID_E'] if isinstance(edge['ID_E'], int) else len(edge['ID_E'])} \n"
            f"({edge['ID_E']}-----{edge['Name_E']} --- {edge['F_PointID']} -----{edge['T_PointID']}) \n"
        )
# print(edges_df.head())

# insert_link_into_database(conn, cursor, edges_df)
