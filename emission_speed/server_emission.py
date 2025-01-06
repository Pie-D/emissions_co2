from flask import Flask, request, jsonify
import os
import requests
from flask_apscheduler import APScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import shutil
import cv2
from ultralytics import YOLO
from tracker import *
import time
import pytz
from flask_cors import CORS
from threading import Thread
timezone = pytz.timezone('America/Toronto')

# Thêm project root vào sys.path
from connection_mysql import *

HOST_CAMERA_VIDEO = "https://www.quebec511.info/Carte/Fenetres/"
class_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
              'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']
red_line_y = 198
blue_line_y = 268
offset = 6
down = {}
up = {}
counter_down = []
counter_up = []

# Kết nối tới database

conn, cursor = connect_db()
cameras = get_list_cameras(conn,cursor)
model = YOLO('yolov8n.pt')
tracker = Tracker()
root_folder = './data_videos'
backup_video_path = './backup_data'
# Định nghĩa hàm emission_results
def emission_results(conn, cursor, type, cameraId, day, hour, view):
    parameter_type = get_pollutant_parameter_database(conn, cursor, type)
    list_vehicle = get_vehicle_speed_by_time(conn, cursor, cameraId, day, hour)
    length = get_length_camera(conn, cursor, cameraId)/1000
    emission = 0
    for vehicle in list_vehicle:
        vehicle_speed = vehicle[2]
        alpha = parameter_type[0][1]
        beta = parameter_type[0][2]
        gamma = parameter_type[0][3]
        delta = parameter_type[0][4]
        epsilon = parameter_type[0][5]
        zeta = parameter_type[0][6]
        eta = parameter_type[0][7]
        emission += (alpha * vehicle_speed**2 + beta * vehicle_speed + gamma + delta/vehicle_speed) / (epsilon * vehicle_speed**2 + zeta * vehicle_speed + eta)
    if view == 1:
        return abs(emission)*length/len(list_vehicle) if len(list_vehicle) != 0 else 0
    return abs(emission)*length

# Tạo Flask app
app = Flask(__name__)
CORS(app)
# def scheduled_crawl_video():
#     try:
#         for camera in cameras:
#             current_date = datetime.now(timezone).strftime("%Y-%m-%d")
#             current_time = datetime.now(timezone).strftime("%H_%M")
#             folder_path = f"./data_videos/{current_date}"

#             # Tạo thư mục nếu chưa tồn tại
#             os.makedirs(folder_path, exist_ok=True)

#             # Đường dẫn để lưu video
#             output_file = os.path.join(folder_path, f"camera_video_id_{camera[0]}_time_{current_time}.mp4")
#             video_url = f"{HOST_CAMERA_VIDEO}{camera[1]}" 
#             # Gửi request đến URL
#             print(video_url)
#             try :
#                 response = requests.get(video_url, stream=True, timeout=10)

#                 # Kiểm tra nếu yêu cầu thành công
#                 if response.status_code == 200:
#                     with open(output_file, "wb") as file:
#                         # Ghi từng phần dữ liệu vào file
#                         for chunk in response.iter_content(chunk_size=8192):
#                             file.write(chunk)
#                     print(f"Video tải xuống thành công! Đã lưu tại: {output_file}")
#                 else:
#                     print(f"Yêu cầu không thành công. Mã lỗi: {response.status_code}")
#             except Exception as e:
#                 print(f"Error: {e}")
#     except Exception as e:
#         print(f"Error in scheduled task: {e}")
# def scheduled_crawl_video():
#     def download_video(camera):
#         try:
#             current_date = datetime.now(timezone).strftime("%Y-%m-%d")
#             current_time = datetime.now(timezone).strftime("%H_%M")
#             folder_path = f"./data_videos/{current_date}"

#             os.makedirs(folder_path, exist_ok=True)
#             output_file = os.path.join(folder_path, f"camera_video_id_{camera[0]}_time_{current_time}.mp4")
#             video_url = f"{HOST_CAMERA_VIDEO}{camera[1]}"
#             response = requests.get(video_url, stream=True, timeout=10)

#             if response.status_code == 200:
#                 with open(output_file, "wb") as file:
#                     for chunk in response.iter_content(chunk_size=8192):
#                         file.write(chunk)
#                 print(f"Tải video thành công: {output_file}")
#             else:
#                 print(f"Yêu cầu không thành công. Mã lỗi: {response.status_code}")
#         except Exception as e:
#             print(f"Lỗi tải video: {e}")

#     # Tải video cho từng camera trong luồng riêng
#     threads = []
#     for camera in cameras:
#         thread = Thread(target=download_video, args=(camera,))
#         thread.start()
#         threads.append(thread)

#     # Đợi tất cả các luồng hoàn thành
#     for thread in threads:
#         thread.join()
# def track_vehicle_speed():
#     for day_folder in os.listdir(root_folder):
#         day_folder_path = os.path.join(root_folder, day_folder)
#         if os.path.isdir(day_folder_path):  # Kiểm tra xem có phải thư mục không
#             print(f"Processing folder: {day_folder}")
#             backup_day_folder_path = os.path.join(backup_video_path, "data_videos", day_folder)
#             if not os.path.exists(backup_day_folder_path):
#                 os.makedirs(backup_day_folder_path)  # Tạo thư mục con tro
            
#             # Duyệt qua các video trong thư mục của ngày đó
#             for video_file in os.listdir(day_folder_path):
#                 video_file_path = os.path.join(day_folder_path, video_file)
#                 if os.path.isfile(video_file_path):  # Kiểm tra xem có phải file không
                    
#                     video_url = f"{root_folder}\\{day_folder}\\{video_file}"
#                     camera_id = int(video_file.split('_')[3])
#                     time_part =  f"{day_folder}:{video_file.split("time_")[1].split(".")[0]}"
#                     part = video_file.split("time_")[1].split(".")[0].split("_")
#                     print(f" - Video file: {video_url}")
#                     cap = cv2.VideoCapture(video_url)
#                     if not cap.isOpened():
#                         print("Không thể mở video từ URL.")
#                         break
#                     # countframe = 0
#                     while cap.isOpened():
#                         #     fps = cap.get(cv2.CAP_PROP_FPS)
#                         #     print(f"Tốc độ khung hình (FPS): {fps}")

#                         # # Lấy tổng số khung hình trong video
#                         #     total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
#                         #     print(f"Tổng số khung hình trong video: {total_frames}")
#                         #     break
#                         ret, frame = cap.read()

#                         if not ret:
#                             print("Video đã kết thúc hoặc không thể đọc khung hình.")
#                             break

#                         # count += 1
#                         # countframe += 1
#                         # if frame % 2 == 0
#                         frame = cv2.resize(frame, (1020, 500))
                       
#                         results = model.predict(frame)

#                         a = results[0].boxes.data

#                         a = a.detach().cpu().numpy()

#                         px = pd.DataFrame(a).astype("float")

#                         list = []

#                         for index, row in px.iterrows():
#                             x1 = int(row[0])
#                             y1 = int(row[1])
#                             x2 = int(row[2])
#                             y2 = int(row[3])
#                             d = int(row[5])
#                             c = class_list[d]
#                             # or 'bus' or 'train' or 'truck'
#                             if c in ['car', 'bicycle', 'motorcycle', 'bus', 'truck']:
#                                 list.append([x1, y1, x2, y2, c])
#                         bbox_id = tracker.update(list)

#                         for bbox in bbox_id:

#                             x3, y3, x4, y4, vehicle_type, id = bbox

#                             cx = int(x3 + x4) // 2

#                             cy = int(y3 + y4) // 2

#                             if red_line_y < (cy+offset) and red_line_y > (cy-offset):

#                                 # current time when vehichle touch the first line
#                                 down[id] = time.time()

#                             if id in down:

#                                 if blue_line_y < (cy+offset) and blue_line_y > (cy-offset):

#                                     # current time when vehicle touch the second line. Also we a re minusing the previous time ( current time of line 1)
#                                     elapsed_time = time.time() - down[id]
#                                     if(elapsed_time == 0):
#                                         elapsed_time = 1
#                                     if counter_down.count(id) == 0:

#                                         counter_down.append(id)

#                                         distance = 10  # meters

#                                         a_speed_ms = distance / elapsed_time

#                                         # this will give kilometers per hour for each vehicle. This is the condition for going downside
#                                         a_speed_kh = a_speed_ms * 3.6

#                                         cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

#                                         cv2.rectangle(frame, (x3, y3), (x4, y4),
#                                                     (0, 255, 0), 2)  # Draw bounding box

#                                         cv2.putText(frame, str(id), (x3, y3),
#                                                     cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

#                                         cv2.putText(frame, str(int(a_speed_kh))+'Km/h', (x4, y4),
#                                                     cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
#                                         insert_speed_into_database(
#                                             conn, cursor, vehicle_type, a_speed_kh, time_part, camera_id,day_folder,part[0],part[1] )
#                             ##### going UP blue line#####

#                             if blue_line_y < (cy+offset) and blue_line_y > (cy-offset):

#                                 up[id] = time.time()

#                             if id in up:

#                                 if red_line_y < (cy+offset) and red_line_y > (cy-offset):

#                                     elapsed1_time = time.time() - up[id]
#                                     if(elapsed1_time == 0):
#                                         elapsed1_time = 1
#                                     # formula of speed= distance/time

#                                     if counter_up.count(id) == 0:
#                                         counter_up.append(id)
#                                         # meters  (Distance between the 2 lines is 10 meters )
#                                         distance1 = 5

#                                         a_speed_ms1 = distance1 / elapsed1_time

#                                         a_speed_kh1 = a_speed_ms1 * 3.6

#                                         cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

#                                         cv2.rectangle(frame, (x3, y3), (x4, y4),
#                                                     (0, 255, 0), 2)  # Draw bounding box

#                                         cv2.putText(frame, str(id), (x3, y3),
#                                                     cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

#                                         cv2.putText(frame, str(int(a_speed_kh1))+'Km/h', (x4, y4),
#                                                     cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
#                                         insert_speed_into_database(
#                                             conn, cursor, vehicle_type, a_speed_kh1, time_part, camera_id, day_folder, part[0], part[1] )
#                         text_color = (0, 0, 0)  # Black color for text

#                         yellow_color = (0, 255, 255)  # Yellow color for background

#                         red_color = (0, 0, 255)  # Red color for lines

#                         blue_color = (255, 0, 0)  # Blue color for lines

#                         cv2.rectangle(frame, (0, 0), (250, 90), yellow_color, -1)

#                         cv2.line(frame, (172, 198), (774, 198), red_color, 2)

#                         cv2.putText(frame, ('Red Line'), (172, 198),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

#                         cv2.line(frame, (8, 268), (927, 268), blue_color, 2)

#                         cv2.putText(frame, ('Blue Line'), (8, 268),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

#                         cv2.putText(frame, ('Going Down - ' + str(len(counter_down))),
#                                     (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

#                         cv2.putText(frame, ('Going Up - ' + str(len(counter_up))), (10, 60),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

#                         # Save frame
#                         # frame_filename = f'detected_frames/frame_{count}.jpg'

#                         # cv2.imwrite(frame_filename, frame)

#                         # out.write(frame)
#                         # print(type(frame))

#                         cv2.imshow("frames", frame)

#                         if cv2.waitKey(1) & 0xFF == ord('q'):

#                             break
                    
#                     cap.release()
#                     try:
#                         # Di chuyển video vào thư mục backup
#                         shutil.move(video_url, backup_day_folder_path)
#                         print(f"Đã di chuyển video {video_file} vào thư mục backup.")
                        
#                         # Xóa video trong thư mục gốc (nếu cần)
#                         # os.remove(video_url)
#                         # print(f"Đã xóa video {video_file} trong thư mục gốc.")
#                     except Exception as e:
#                         print(f"Không thể di chuyển {video_file}: {e}")

# # Cấu hình APScheduler
# class Config:
#     SCHEDULER_API_ENABLED = True

# app.config.from_object(Config)

# scheduler = APScheduler()
# scheduler.init_app(app)
# scheduler.start()
# # Thêm job vào scheduler
# scheduler.add_job(
#     id='ScheduledTask',
#     func=scheduled_crawl_video,
#     trigger=IntervalTrigger(minutes=10)

# )
# scheduler.add_job(
#     id='ScheduledTask1',
#     func=track_vehicle_speed,
#     trigger=IntervalTrigger(minutes=15)
# )
# def emission_results(conn, cursor, type, cameraId, day, hour):
#     parameter_type = get_pollutant_parameter_database(conn, cursor, type)
#     list_vehicle = get_vehicle_speed_by_time(conn, cursor, cameraId, day, hour)
#     emission = 0
#     print(hour, "--------", type, "--------", len(list_vehicle))
#     for vehicle in list_vehicle:
#         vehicle_speed = vehicle[2]
#         alpha = parameter_type[0][1]
#         beta = parameter_type[0][2]
#         gamma = parameter_type[0][3]
#         delta = parameter_type[0][4]
#         epsilon = parameter_type[0][5]
#         zeta = parameter_type[0][6]
#         eta = parameter_type[0][7]
#         emission += abs((alpha * vehicle_speed**2 + beta * vehicle_speed + gamma + delta/vehicle_speed) / (epsilon * vehicle_speed**2 + zeta * vehicle_speed + eta))
#     result = (emission/ len(list_vehicle)) if len(list_vehicle) != 0 else 0
#     return result
# Route để gọi hàm emission_results
@app.route('/emission_day', methods=['GET'])
def calculate_emission_day():
    try:
        # Lấy tham số từ request
        cameraId = int(request.args.get('cameraId'))
        day = request.args.get('day')
        viewType = request.args.get('viewType')
        if viewType == 'average':
            view = 1
        else :
            view = 0
        hours = list(range(24))
        CO = [emission_results(conn, cursor, 'CO', cameraId, day, i, view) for i in hours]
        print("CO")
        NOx = [emission_results(conn, cursor, 'NOx', cameraId, day, i, view) for i in hours]
        print("NOx")
        VOC = [emission_results(conn, cursor, 'VOC', cameraId, day, i, view) for i in hours]
        print("VOC")
        CO2 = [emission_results(conn, cursor, 'CO2', cameraId, day, i, view) for i in hours]
        return jsonify({'time': hours, 'CO': CO, 'NOx': NOx, 'VOC': VOC, 'CO2': CO2})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/emission', methods=['GET'])
def calculate_emission():
    try:
        # Lấy tham số từ request
        type = request.args.get('type')
        cameraId = int(request.args.get('cameraId'))
        day = request.args.get('day')
        hour = int(request.args.get('hour'))

        # Gọi hàm emission_results
        emission = emission_results(conn, cursor, type, cameraId, day, hour)
        return jsonify({"emission": emission,
                        "emission_unit": "g/km",})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Chạy server
if __name__ == '__main__':
    # print(scheduler.get_jobs())
    app.run(debug=False, host='0.0.0.0', port=5000)
