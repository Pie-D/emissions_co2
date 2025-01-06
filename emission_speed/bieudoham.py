import matplotlib.pyplot as plt
import numpy as np
import random
import os
import requests
import sys
import time
from connection_mysql import *
conn, cursor = connect_db()
get_length_camera(conn, cursor, 16)
# Hệ số của CO2 từ bảng

# Hàm tính toán E_pj
def emission_intensity(v, parameter_type):
    vehicle_speed = v
    alpha = parameter_type[0][1]
    beta = parameter_type[0][2]
    gamma = parameter_type[0][3]
    delta = parameter_type[0][4]
    epsilon = parameter_type[0][5]
    zeta = parameter_type[0][6]
    eta = parameter_type[0][7]
    emission = abs((alpha * vehicle_speed**2 + beta * vehicle_speed + gamma + delta/vehicle_speed) / (epsilon * vehicle_speed**2 + zeta * vehicle_speed + eta))
    print(emission)
    return emission*0.8
# # Dải vận tốc
print(emission_intensity(55.4,get_pollutant_parameter_database(conn, cursor, 'NOx') ))
# # Hàm vẽ biểu đồ cho từng khí
# def plot_pollutant(pollutant_name):
#     coeffs = get_pollutant_parameter_database(conn, cursor, pollutant_name)
#     v = get_speeds_by_time_and_camera(conn, cursor,16,'2024-12-14')
#     speeds = [item[0] for item in v]
#     time.sleep(10)
#     E_pj = emission_intensity(v, coeffs)
#     # Vẽ đồ thị
#     plt.figure(figsize=(12, 6))
    
#     # (a) Dữ liệu thực tế và đường khớp
#     plt.subplot(1, 2, 1)
#     plt.plot(speeds, E_pj, label='Fitting curve', color='orange')
#     plt.scatter(speeds, E_pj, label='Original data', color='blue', s=10)  # Dữ liệu giả định
#     plt.title(f'Actual relationship between {pollutant_name} traffic \n emission intensity and average speed')
#     plt.xlabel('Average speed (km/h)')
#     plt.ylabel(f'{pollutant_name} traffic emission intensity (g/veh)')
#     plt.legend()
#     plt.grid()
    
#     # (b) Đường lý thuyết
#     plt.subplot(1, 2, 2)
#     plt.plot(v, E_pj, label='Theoretical Curve', color='red')
#     plt.title(f'Theoretical relationship between {pollutant_name} traffic \n  emission intensity and average speed')
#     plt.xlabel('Average speed (km/h)')
#     plt.ylabel(f'{pollutant_name} traffic emission intensity (g/veh)')
#     plt.legend()
#     plt.grid()
    
#     # Hiển thị biểu đồ
#     plt.tight_layout()
#     plt.show()

# # Vẽ cho từng khí
# # plot_pollutant('CO')
# # plot_pollutant('VOC')
# # plot_pollutant('NOx')
# plot_pollutant('CO2')