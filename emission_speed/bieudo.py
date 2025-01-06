import matplotlib.pyplot as plt
import numpy as np
import random
import os
import requests
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(project_root)
from emissions_co2.emission_speed.connection_mysql import *
conn, cursor = connect_db()
def emission_results(conn, cursor, type, cameraId, day, hour):
    parameter_type = get_pollutant_parameter_database(conn, cursor, type)
    list_vehicle = get_vehicle_speed_by_time(conn, cursor, cameraId, day, hour)
    emission = 0
    print(hour, "--------", type, "--------", len(list_vehicle))
    for vehicle in list_vehicle:
        vehicle_speed = vehicle[2]
        alpha = parameter_type[0][1]
        beta = parameter_type[0][2]
        gamma = parameter_type[0][3]
        delta = parameter_type[0][4]
        epsilon = parameter_type[0][5]
        zeta = parameter_type[0][6]
        eta = parameter_type[0][7]
        emission += abs((alpha * vehicle_speed**2 + beta * vehicle_speed + gamma + delta/vehicle_speed) / (epsilon * vehicle_speed**2 + zeta * vehicle_speed + eta))
    return abs(emission)/len(list_vehicle)
hours = list(range(24))
cameraId = 7
day =  '2024-12-14'
[print(i) for i in hours]
CO = [emission_results(conn, cursor, 'CO', cameraId, day, i) for i in hours]
print("CO")
NOx = [emission_results(conn, cursor, 'NOx', cameraId, day, i) for i in hours]
print("NOx")
VOC = [emission_results(conn, cursor, 'VOC', cameraId, day, i) for i in hours]
print("VOC")
CO2 = [emission_results(conn, cursor, 'CO2', cameraId, day, i) for i in hours]
print("CO2")
# Tạo dữ liệu cộng dồn
CO_stack = np.array(CO)
NOx_stack = np.array(NOx) + CO_stack
VOC_stack = np.array(VOC) + NOx_stack

# Tạo figure và trục
fig, ax1 = plt.subplots()

# Biểu đồ cột (bar)
ax1.bar(hours, CO, label='CO', color='orange', hatch='', edgecolor='black')
ax1.bar(hours, NOx, label='NOx', color='blue', hatch='\\', edgecolor='black', bottom=CO_stack)
ax1.bar(hours, VOC, label='VOC', color='yellow', edgecolor='black', bottom=NOx_stack)

# Trục Y bên trái (cho CO, NOx, VOC)
ax1.set_xlabel('Time (1 hour)')
ax1.set_ylabel('Pollutant traffic emission intensity (g/veh)')
ax1.set_xticks(hours)
ax1.legend(loc='upper left')
ax1.grid(axis='y', linestyle='--', alpha=0.7)

ax1.set_ylim(0, max(VOC_stack) + 0.2)
# Trục Y bên phải (cho CO2)
ax2 = ax1.twinx()
ax2.plot(hours, CO2, label='CO2', color='red', linewidth=2)
ax2.set_ylabel('CO2 traffic emission intensity (g/veh)')
ax2.legend(loc='upper right')

ax2.set_ylim(0, max(CO2) + 50) 
# Hiển thị
plt.title(f'Traffic Emission Intensity {day} camera id: {cameraId}')
plt.show()
