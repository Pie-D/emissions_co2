import requests
import os
from datetime import datetime
import sys
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(project_root)
from emissions_co2.emission_speed.connection_mysql import * 
# URL của video
HOST_CAMERA_VIDEO = "https://www.quebec511.info/Carte/Fenetres/"


conn, cursor = connect_db()

cameras = get_list_cameras(conn,cursor)
# Lấy ngày giờ hiện tại để tạo tên thư mục
while True :
    for camera in cameras:
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H_%M")
        folder_path = f"./data_videos/{current_date}"

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(folder_path, exist_ok=True)

        # Đường dẫn để lưu video
        output_file = os.path.join(folder_path, f"camera_video_id_{camera[0]}_time_{current_time}.mp4")
        video_url = f"{HOST_CAMERA_VIDEO}{camera[1]}" 
        # Gửi request đến URL
        response = requests.get(video_url, stream=True)

        # Kiểm tra nếu yêu cầu thành công
        if response.status_code == 200:
        # Mở file ở chế độ ghi nhị phân
            with open(output_file, "wb") as file:
                # Ghi từng phần dữ liệu vào file
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Video tải xuống thành công! Đã lưu tại: {output_file}")
        else:
            print(f"Yêu cầu không thành công. Mã lỗi: {response.status_code}")

    print("Đợi 30 phút trước khi tải xuống lần tiếp theo...")

    time.sleep(900)
