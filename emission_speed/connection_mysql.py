import mysql.connector
from datetime import datetime
import pandas as pd


def connect_db():
    db_config = {
        'user': 'root',
        'password': 'Quyendiep2002',
        'host': 'localhost',
        'database': 'emissions',
    }
    conn = mysql.connector.connect(**db_config)
    return conn, conn.cursor()


def insert_speed_into_database(conn, cursor, vehicle_type, speed, time,camera_id, day, hour, minute):
    insert_query = """
    INSERT INTO vehicle_speed (vehicle_type, speed, time, camera_id, day, hour, minute)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (vehicle_type, speed, time, camera_id, day, hour, minute))
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

def get_pollutant_parameter_database(conn, cursor, pollutant):
    get_pollutan_parameter_query = """
        SELECT * FROM pollutant_parameters WHERE pollutant = %s;
        """
    cursor.execute(get_pollutan_parameter_query, (pollutant,))
    result = cursor.fetchall()
    return result

def get_vehicle_speed(conn, cursor, camera_id):
    get_vehicle_speed_by_camera_id = """
        Select * from  vehicle_speed where camera_id = %s;
    """  
    cursor.execute(get_vehicle_speed_by_camera_id, (camera_id,))
    result  = cursor.fetchall()
    return result

def get_list_cameras(conn, cursor):
    list_cameras_query = """
    SELECT * FROM cameras;
    """
    cursor.execute(list_cameras_query)
    result = cursor.fetchall()
    return result

def get_vehicle_speed_by_time(conn, cursor, camera_id, day, hour):
    query = ''
    if hour == -1 :
        query = """
            Select * from  vehicle_speed where camera_id = %s and day = %s;
        """  
        cursor.execute(query, (camera_id,day))
        result  = cursor.fetchall()
    else :
        query = """
            Select * from  vehicle_speed where camera_id = %s and day = %s and hour = %s ;
        """
        cursor.execute(query, (camera_id,day,hour))
        result  = cursor.fetchall()
    return result

def get_speeds_by_time_and_camera(conn, cursor, camera_id, day):
    query = """
    SELECT speed
    FROM vehicle_speed
    WHERE day = %s
    AND camera_id = %s
    ORDER BY speed ASC; 

    """
    cursor.execute(query, (day, camera_id))
    result = cursor.fetchall()
    print(result)
    return result
def get_length_camera(conn, cursor, camera_id):
    query = """
    SELECT length_next
    FROM cameras
    WHERE id = %s
    """
    cursor.execute(query,(camera_id,))
    result = cursor.fetchone()[0]
    print(result)
    return int(result)