import mysql.connector
from datetime import datetime
import pandas as pd


def connect_db():
    db_config = {
        'user': 'root',
        'password': 'Diepdz123..',
        'host': 'localhost',
        'database': 'emissions',
    }
    conn = mysql.connector.connect(**db_config)
    return conn, conn.cursor()


def insert_speed_into_database(conn, cursor, vehicle_type, speed, time):
    formatted_time = datetime.fromtimestamp(
        time).strftime('%Y-%m-%d %H:%M:%S')
    insert_query = """
    INSERT INTO vehicle_speed (vehicle_type, speed, time)
    VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (vehicle_type, speed, formatted_time))
    conn.commit()


def insert_node_into_database(conn, cursor, nodes):
    insert_node_query = """
    INSERT INTO node (ID_P, Longitude, Latitude)
    VALUES (%s, %s, %s);
    """
    for index, node in nodes.iterrows():
        cursor.execute(insert_node_query,
                       (node['ID_P'], node['Longitude'], node['Latitude']))
    conn.commit()


def insert_link_into_database(conn, cursor, edges):
    insert_link_query = """
    INSERT INTO link (ID_E, Name_E, F_PointID, T_PointID, Length, Two_way, Lane_number)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """


# Duyệt qua dataframe `edges` và chèn dữ liệu vào MySQL
    for _, edge in edges.iterrows():
        print(edge)
        cursor.execute(insert_link_query, (edge['ID_E'], edge['Name_E'],
                                           edge['F_PointID'], edge['T_PointID'], edge['Length'], edge['Two_way'], edge['Lane_number']))

# Lưu các thay đổi
    conn.commit()
