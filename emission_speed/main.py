import time
import ultralytics
import shutil
import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import os
import sys

from connection_mysql import * 
import numpy as np
# https: // sfs1.roadsummary.com/rtplive/CAM047/playlist.m3u8
# Khởi tạo model YOLO
model = YOLO('yolov5su.pt')

# Danh sách các lớp đối tượng mà YOLO có thể nhận diện
class_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
              'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

# Khởi tạo đối tượng Tracker
tracker = Tracker()
model = YOLO("yolov8n.pt")
cap=cv2.VideoCapture('highway.mp4')
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (1020, 500))

    results = model.predict(frame)
    a = results[0].boxes.data
    a = a.detach().cpu().numpy()
    px = pd.DataFrame(a).astype("float")
    # print(px)
    list = []
    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]
        if c in ['car', 'bicycle', 'motorcycle', 'bus', 'truck']:
            list.append([x1, y1, x2, y2, c])
    bbox_id = tracker.update(list)

    for bbox in bbox_id:
        x3, y3, x4, y4,vehicle_type, id = bbox
        cx = int(x3 + x4) // 2
        cy = int(y3 + y4) // 2
        cv2.circle(frame,(cx,cy),4,(0,0,255), -1)
        cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
        # cv2.putText(frame, str(id), (x3, y3 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # cv2.putText(frame, f"{cx}, {cy}", (x3, y3 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.imshow("frame", frame)
    if cv2.waitKey(0)&0xFF==27 :
        break
cap.release()
cv2.destroyAllWindows