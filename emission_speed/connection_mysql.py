import mysql.connector
from datetime import datetime


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
