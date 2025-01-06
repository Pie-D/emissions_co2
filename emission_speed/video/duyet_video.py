import os
import sys
import datetime
import cv2
import ultralytics
from ultralytics import YOLO
from tracker import *
import pandas as pd
import time
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(project_root)
from emissions_co2.emission_speed.connection_mysql import * 
con, cursor = connect_db()
red_line_y = 198
blue_line_y = 268
offset = 6
down = {}
up = {}
counter_down = []
counter_up = []

model = YOLO('yolov5su.pt')
class_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
              'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']
tracker = Tracker()
# Đường dẫn đến thư mục chứa video
current_date = datetime.now().strftime("%Y-%m-%d")
current_time = datetime.now().strftime("%H_%M")
day_folder_path = f"../data_videos/{current_date}"
for video_file in sorted(os.listdir(day_folder_path)):
    video_file_path = os.path.join(day_folder_path, video_file)
    if os.path.isfile(video_file_path):  # Kiểm tra xem có phải file không
        print(f" - Video file: {video_file}")
        video_url = f"{day_folder_path}\\{video_file}"
        camera_id = int(video_file.split('_')[3])
        time_part =  f"{current_date}:{video_file.split("time_")[1].split(".")[0]}"
        part = video_file.split("time_")[1].split(".")[0].split("_")
# if not os.path.exists('detected_frames'):
#     os.makedirs('detected_frames')

# fourcc = cv2.VideoWriter_fourcc(*'XVID')

# out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1020, 500))
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            print("Không thể mở video từ URL.")
            break
        # countframe = 0
        while cap.isOpened():
            #     fps = cap.get(cv2.CAP_PROP_FPS)
            #     print(f"Tốc độ khung hình (FPS): {fps}")

            # # Lấy tổng số khung hình trong video
            #     total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            #     print(f"Tổng số khung hình trong video: {total_frames}")
            #     break
            ret, frame = cap.read()

            if not ret:
                print("Video đã kết thúc hoặc không thể đọc khung hình.")
                break

            # count += 1
            # countframe += 1
            # if frame % 2 == 0
            frame = cv2.resize(frame, (1020, 500))
            # kernel = np.array([[0, -1, 0],
            #                 [-1, 5, -1],
            #                 [0, -1, 0]])
            # # frame = cv2.medianBlur(frame, 5)
            # # Áp dụng bộ lọc sắc nét vào ảnh
            # frame = cv2.filter2D(frame, -1, kernel)

            # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            # sharpened = cv2.filter2D(frame, -1, kernel)

            # # Áp dụng bộ lọc trung vị
            # median_filtered = cv2.medianBlur(sharpened, 5)

            # # Tăng cường độ tương phản
            # lab = cv2.cvtColor(median_filtered, cv2.COLOR_BGR2LAB)
            # l, a, b = cv2.split(lab)
            # clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            # cl = clahe.apply(l)
            # enhanced = cv2.merge((cl, a, b))
            # enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

            # # Thay đổi kích thước cho YOLO
            # frame = cv2.resize(frame, (416, 416))
            # image_for_yolo = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)

            # cv2.imshow('Sharpened Image', frame)
            results = model.predict(frame)

            a = results[0].boxes.data

            a = a.detach().cpu().numpy()

            px = pd.DataFrame(a).astype("float")

            list = []

            for index, row in px.iterrows():
                x1 = int(row[0])
                y1 = int(row[1])
                x2 = int(row[2])
                y2 = int(row[3])
                d = int(row[5])
                c = class_list[d]
                # or 'bus' or 'train' or 'truck'
                if c in ['car', 'bicycle', 'motorcycle', 'bus', 'truck']:
                    list.append([x1, y1, x2, y2, c])
            bbox_id = tracker.update(list)

            for bbox in bbox_id:

                x3, y3, x4, y4, vehicle_type, id = bbox

                cx = int(x3 + x4) // 2

                cy = int(y3 + y4) // 2

                if red_line_y < (cy+offset) and red_line_y > (cy-offset):

                    # current time when vehichle touch the first line
                    down[id] = time.time()

                if id in down:

                    if blue_line_y < (cy+offset) and blue_line_y > (cy-offset):

                        # current time when vehicle touch the second line. Also we a re minusing the previous time ( current time of line 1)
                        elapsed_time = time.time() - down[id]
                        if(elapsed_time == 0):
                            elapsed_time = 1
                        if counter_down.count(id) == 0:

                            counter_down.append(id)

                            distance = 10  # meters

                            a_speed_ms = distance / elapsed_time

                            # this will give kilometers per hour for each vehicle. This is the condition for going downside
                            a_speed_kh = a_speed_ms * 3.6

                            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                            cv2.rectangle(frame, (x3, y3), (x4, y4),
                                        (0, 255, 0), 2)  # Draw bounding box

                            cv2.putText(frame, str(id), (x3, y3),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

                            cv2.putText(frame, str(int(a_speed_kh))+'Km/h', (x4, y4),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                            insert_speed_into_database(
                                con, cursor, vehicle_type, a_speed_kh, time_part, camera_id,current_date,part[0],part[1] )
                ##### going UP blue line#####

                if blue_line_y < (cy+offset) and blue_line_y > (cy-offset):

                    up[id] = time.time()

                if id in up:

                    if red_line_y < (cy+offset) and red_line_y > (cy-offset):

                        elapsed1_time = time.time() - up[id]
                        if(elapsed1_time == 0):
                            elapsed1_time = 1
                        # formula of speed= distance/time

                        if counter_up.count(id) == 0:
                            counter_up.append(id)
                            # meters  (Distance between the 2 lines is 10 meters )
                            distance1 = 5

                            a_speed_ms1 = distance1 / elapsed1_time

                            a_speed_kh1 = a_speed_ms1 * 3.6

                            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

                            cv2.rectangle(frame, (x3, y3), (x4, y4),
                                        (0, 255, 0), 2)  # Draw bounding box

                            cv2.putText(frame, str(id), (x3, y3),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)

                            cv2.putText(frame, str(int(a_speed_kh1))+'Km/h', (x4, y4),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)
                            insert_speed_into_database(
                                con, cursor, vehicle_type, a_speed_kh1, time_part, camera_id, current_date, part[0], part[1] )
            text_color = (0, 0, 0)  # Black color for text

            yellow_color = (0, 255, 255)  # Yellow color for background

            red_color = (0, 0, 255)  # Red color for lines

            blue_color = (255, 0, 0)  # Blue color for lines

            cv2.rectangle(frame, (0, 0), (250, 90), yellow_color, -1)

            cv2.line(frame, (172, 198), (774, 198), red_color, 2)

            cv2.putText(frame, ('Red Line'), (172, 198),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

            cv2.line(frame, (8, 268), (927, 268), blue_color, 2)

            cv2.putText(frame, ('Blue Line'), (8, 268),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

            cv2.putText(frame, ('Going Down - ' + str(len(counter_down))),
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

            cv2.putText(frame, ('Going Up - ' + str(len(counter_up))), (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

            # Save frame
            # frame_filename = f'detected_frames/frame_{count}.jpg'

            # cv2.imwrite(frame_filename, frame)

            # out.write(frame)
            # print(type(frame))

            cv2.imshow("frames", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):

                break
        cap.release()
        # out.release()
