import os
#os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/home/orangepi/.local/lib/python3.10/site-packages/cv2/qt/plugins'
import sys
import cv2
import time
import librosa
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QTimer
from ui_main import Ui_Game
from ultralytics import YOLO
import numpy as np
import pygame
import threading
from threading import Timer
# from pythonosc import udp_client # 如果不需要 OSC 通訊，可以註解掉
import matplotlib.pyplot as plt
import random_color # 確保這個文件存在且內容正確

# 初始化 Pygame 混音器
pygame.mixer.init()

# 假設 logger 已經定義或者提供一個簡單的替代
class SimpleLogger:
    def info(self, message):
        print(f"[INFO] {message}")
    def error(self, message):
        print(f"[ERROR] {message}")
    def warning(self, message):
        print(f"[WARN] {message}")
logger = SimpleLogger()


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.total_score = 0
        self.prev_time = 0
        self.sound_dict = {}

        self.aa = self.bb = False
        self.temp2 = self.temp3 = 0

        self.fpstemp = []
        self.frame_count = 0
        self.display_fps = 0.0

        self.qt_image = None
        self.reset_fire = True
        self.reset_blue_fire = True

        self.beat = 0.0
        self.beat_times = []
        self.pose_timing = 0
        self.music_start_time = 0.0
        self.beat_interval = 0.0
        self.cool_time = 0.6
        self.combo = 0
        self.combo_mult = 0
        self.ui = Ui_Game()
        self.ui.setupUi(self)

        self.gif = QMovie(r"/home/orangepi/Desktop/Merry_healthy/gif素材/red_fire.gif")
        self.bluegif = QMovie(r"/home/orangepi/Desktop/Merry_healthy/gif素材/blue_fire.gif")

        # --- 模型載入 (使用 YOLOv8 姿勢估計模型) ---
        # 注意：這裡使用 PyTorch .pt 模型進行演示。
        # 如果你的模型是 NCNN 格式，請確保它是為姿勢估計轉換的 NCNN 模型，
        # 並且 ultralytics 庫支援載入和執行它。
        # 你的原始代碼中是 'weight/yolo11s-pose_rknn_model'，
        # 如果這是 NCNN/RKNN 模型，YOLO 類別可能需要針對特定執行時環境（例如 RKNN Toolkit）進行配置。
        # 這裡為了簡單起見，直接使用 ultralytics 支援的 .pt 或其能識別的模型。
        # 如果你的模型是 RKNN 格式且 YOLO 類別無法直接載入，你可能需要額外的 RKNN 推理代碼。
        self.model = YOLO("./yolo11n-pose_ncnn_model", task="pose") # 假設你的姿勢模型是 .pt 格式
        # 如果是 NCNN 模型，並且 ultralytics 可以直接載入，則使用：
        # self.model = YOLO(r'weight/yolo11s-pose_ncnn_model', task="pose")
        logger.info(f"Using device: {self.model.device}")
        # --- End Model Loading ---

        self.video_cap = self.camera_cap = None
        self.lock1 = self.lock2 = self.lock3 = self.lock4 = self.lock5 = True

        self.is_running = False
        self.ui.stopping.setText("stop")

        self.video_timer = QtCore.QTimer()
        self.video_timer.timeout.connect(self.update_video_frame)

        self.camera_timer = QtCore.QTimer()
        self.camera_timer.timeout.connect(self.update_camera_frame)

        self.ui.pushButton.clicked.connect(self.start_all)
        self.ui.stopping.clicked.connect(self.toggle_playback)

        # COCO Keypoint connections (for human pose)
        self.skeleton_connections = [
            (0, 1), (0, 2), (1, 3), (2, 4),      # Head, Neck, Shoulders, Elbows
            (5, 6), (5, 7), (6, 8), (7, 9),      # Shoulders, Hips, Knees, Ankles
            (10, 11), (11, 12), (12, 13), (13, 14), # (Left, Right) Hip, Knee, Ankle
            (5, 11), (6, 12) # For torso connection (left shoulder to left hip, right shoulder to right hip)
        ]
        # Keypoint colors (you can define specific colors for different keypoints)
        self.keypoint_colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255)] * 3


    def calculate_angle(self, a, b, c):  ##計算關節點角度的function
        a = np.array(a)  # 頭
        b = np.array(b)  # 中間點
        c = np.array(c)  # 尾

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)  # 徑轉度
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def play_sound(self, choose_sound):
        temp1 = choose_sound
        if temp1 == self.temp2:
            return
        sound_dict = {'1': r'/home/orangepi/Desktop/Merry_healthy/Voice/continue.mp3', '2': r'/home/orangepi/Desktop/Merry_healthy/Voice/A2.mp3',
                      '3': r'/home/orangepi/Desktop/Merry_healthy/Voice/A3.mp3', '4': r'/home/orangepi/Desktop/Merry_healthy/Voice/A4.mp3',
                      '5': r'/home/orangepi/Desktop/Merry_healthy/Voice/A5.mp3',
                      '6': r'/home/orangepi/Desktop/Merry_healthy/Voice/蟋蟀V3_降噪正規化_左.wav', '7': r'/home/orangepi/Desktop/Merry_healthy/Voice/蟋蟀V3_降噪正規化_右.wav' }

        pygame.mixer.Sound(sound_dict[choose_sound]).play()
        self.temp2 = choose_sound

    def play_sound_1(self, choose_sound):
        temp1 = choose_sound
        if temp1 == self.temp3:
            return
        sound_dict = {'1': r'/home/orangepi/Desktop/Merry_healthy/Voice/continue.mp3', '2': r'/home/orangepi/Desktop/Merry_healthy/Voice/A2.mp3',
                      '3': r'/home/orangepi/Desktop/Merry_healthy/Voice/A3.mp3', '4': r'/home/orangepi/Desktop/Merry_healthy/Voice/A4.mp3',
                      '5': r'/home/orangepi/Desktop/Merry_healthy/Voice/A5.mp3',
                      '6': r'/home/orangepi/Desktop/Merry_healthy/Voice/蟋蟀V3_降噪正規化_左.wav', '7': r'/home/orangepi/Desktop/Merry_healthy/Voice/蟋蟀V3_降噪正規化_右.wav' }

        pygame.mixer.music.load(sound_dict[choose_sound])
        pygame.mixer.music.play()
        self.temp3 = choose_sound

    def play_sound_2(self, choose_sound):
        temp1 = choose_sound
        if temp1 == self.temp3:
            return
        sound_dict = {'1': r'/home/orangepi/Desktop/Merry_healthy/Voice/continue.mp3', '2': r'/home/orangepi/Desktop/Merry_healthy/Voice/A2.mp3',
                      '3': r'/home/orangepi/Desktop/Merry_healthy/Voice/A3.mp3', '4': r'/home/orangepi/Desktop/Merry_healthy/Voice/A4.mp3',
                      '5': r'/home/orangepi/Desktop/Merry_healthy/Voice/A5.mp3',
                      '6': r'/home/orangepi/Desktop/Merry_healthy/Voice/蟋蟀V3_降噪正規化_左.wav', '7': r'/home/orangepi/Desktop/Merry_healthy/Voice/蟋蟀V3_降噪正規化_右.wav' }
        pygame.mixer.Sound(sound_dict[choose_sound]).play()
        self.temp3 = choose_sound

    def stop_sound(self):      #終止持續音效的function(動作一)
        pygame.mixer.music.stop()
        self.temp3 = None
    def wait(self,num):
        # time.sleep(0.2)
        self.play_sound_2(num)
    def start_score_timer(self):
        self.score_timer = QtCore.QTimer()
        self.score_timer.timeout.connect(self.show_score)
        self.score_timer.start(100)  # 每 100 毫秒更新一次（可依需求調整）

    def show_score(self):
        self.ui.label_title.setText(f"Score: {float(self.total_score)}")
    def play_music(self, music_path):       ##播放背景音樂的function
        y, sr = librosa.load(music_path)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        self.beat_times = librosa.frames_to_time(beats, sr=sr)  ##先等librosa處理完再開始播歌
        self.beat_interval = self.beat_times[10] - self.beat_times[9]  ##計算拍子間隔
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play()

        threading.Thread(target=self.play_beat_in_background, args=(self.beat_times,), daemon=True).start()


    def play_beat_in_background(self, beat_times):
        self.music_start_time = time.time()
        beat_count = 0
        for i, self.beat in enumerate(beat_times):
            if i % 2 != 0:
                continue  # 每兩拍一次

            wait_time = self.beat - (time.time() - self.music_start_time)
            if wait_time > 0:  ##等到拍點
                time.sleep(wait_time)
            beat_count = (beat_count % 4) + 1  # 拍點1~4
            dots = "🔴  " * beat_count
            self.ui.label_beat.setText(dots)
            self.ui.label_combo.setText(f"Combo ✖{self.combo}")
            if abs(self.beat - self.pose_timing) > self.beat_interval * 0.9 :  ##如果沒做動作
                self.combo = 0
                self.ui.label_combo.setText(f"Combo ✖{self.combo}")
            if self.combo < 3:    ####分數combo加成
                self.bluegif.stop()
                self.ui.label_fire.clear()

    def start_all(self):
        # pipeline = "v4l2src device=/dev/video0 ! videoconvert ! appsink" # Ubuntu GStreamer pipeline
        # For general webcam, use index 0 or 1 etc.
        self.video_cap = cv2.VideoCapture(r"/home/orangepi/Desktop/Merry_healthy/test (1).mp4")
        music_path = r"/home/orangepi/Desktop/Merry_healthy/song_low.mp3"
        threading.Thread(target=self.play_music, args=(music_path,), daemon=True).start() # 確保音樂在獨立線程中播放
        
        # 嘗試使用 GStreamer pipeline，如果不行則 fallback 到預設
        try:
            self.camera_cap = cv2.VideoCapture("v4l2src device=/dev/video0 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
            if not self.camera_cap.isOpened():
                raise IOError("GStreamer failed, trying default camera.")
        except IOError:
            logger.warning("GStreamer camera capture failed, falling back to default OpenCV capture.")
            self.camera_cap = cv2.VideoCapture(0) # For webcam (usually index 0)

        # self.camera_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        # self.camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # self.camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        # self.camera_cap.set(cv2.CAP_PROP_FPS, 35)
        self.start_score_timer()
        self.video_timer.start(33)
        self.camera_timer.start(20)
        self.is_running = True
        self.ui.stopping.setText("stop")

    def toggle_playback(self):
        self.is_running = not self.is_running
        self.ui.stopping.setText("stop" if self.is_running else "continue")

    def update_video_frame(self):
        if not self.is_running or self.video_cap is None:
            return
        ret, frame = self.video_cap.read()
        if ret:
            self.display_frame(self.ui.label_left, frame)

    def plot_keypoints_and_skeleton(self, frame, keypoints_data, box_data, conf_scores, class_ids):
        # Draw keypoints and skeleton for each detected person
        for person_idx, kps_xy in enumerate(keypoints_data):
            person_score = conf_scores[person_idx]
            
            # 根據 min_conf 篩選
            min_conf = 0.5 # 假設用於姿勢估計的最小信心度
            if person_score < min_conf:
                continue

            # 繪製邊界框
            x1, y1, x2, y2 = map(int, box_data[person_idx])
            label = self.model.names[int(class_ids[person_idx])] if hasattr(self.model, 'names') else "person"
            color = random_color.get_random_color(label) # 使用 random_color 模組

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2) # rectangle_thickness = 2
            text = f"{label} {person_score:.2f}"
            (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2) # text_thickness = 2
            cv2.rectangle(frame, (x1, y1 - h - 5), (x1 + w, y1), color, -1)
            cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)


            # 繪製關鍵點
            for kp_idx, (x, y) in enumerate(kps_xy):
                x_int, y_int = int(x), int(y)
                if x_int > 0 and y_int > 0:
                    cv2.circle(frame, (x_int, y_int), 5, self.keypoint_colors[kp_idx % len(self.keypoint_colors)], -1)

            # 繪製骨架連接
            for connection in self.skeleton_connections:
                kp1_idx, kp2_idx = connection
                if kp1_idx < len(kps_xy) and kp2_idx < len(kps_xy):
                    kp1_x, kp1_y = int(kps_xy[kp1_idx][0]), int(kps_xy[kp1_idx][1])
                    kp2_x, kp2_y = int(kps_xy[kp2_idx][0]), int(kps_xy[kp2_idx][1])

                    if kp1_x > 0 and kp1_y > 0 and kp2_x > 0 and kp2_y > 0:
                        cv2.line(frame, (kp1_x, kp1_y), (kp2_x, kp2_y), (0, 255, 255), 2) # 黃色線條，thickness = 2


    def score_cal(self, dif_time):
        best = self.beat_interval * 0.2  ##最佳拍點  1
        nice = self.beat_interval * 0.4  #2
        not_bad = self.beat_interval * 0.8#3
        print(f"Beat Interval: {self.beat_interval:.2f}s, Best: {best:.2f}s, Nice: {nice:.2f}s, Not Bad: {not_bad:.2f}s")

        if self.combo < 5:    ####分數combo加成
            self.combo_mult = 1.0
        elif self.combo < 9:
            self.combo_mult = 1.1
        elif self.combo < 13:
            self.combo_mult = 1.25
        else:
            self.combo_mult = 1.5

        if abs(dif_time) < best:           ##best跟nice才有combo加成(self.combo_mult)
            self.total_score += 3 * self.combo_mult
            self.combo += 1
            logger.info("Perfect!")
        elif abs(dif_time) <= nice:
            self.total_score += 2 * self.combo_mult
            self.combo += 1
            logger.info("Good!")
        elif abs(dif_time) <= not_bad:
            self.total_score += 1
            self.combo = 0
            logger.info("OK!")
        else:
            self.combo = 0
            logger.info("Miss!")
        QTimer.singleShot(0, self.update_fire_effect)


    def update_fire_effect(self):
        if self.combo > 5:
            self.ui.label_fire.setMovie(self.gif)
            self.gif.start()
        elif self.combo > 3:
            self.ui.label_fire.setMovie(self.bluegif)
            self.bluegif.start()
        else:
            self.gif.stop()
            self.bluegif.stop()
            self.ui.label_fire.clear()


    def unlock(self, number):    ##解決動作維持導致多次誤觸問題的function
        if number == '1':
            self.lock1 = True
        elif number == '2':
            self.lock2 = True
        elif number == '3':
            self.lock3 = True
        elif number == '4':
            self.lock4 = True
        elif number == '5':
            self.lock5 = True

    def update_camera_frame(self):
        if not self.is_running or self.camera_cap is None:
            return
        ret, frame = self.camera_cap.read()
        if ret:
            self.frame_count += 1

            if self.frame_count >= 5:        # 五幀更新一次FPS
                curr_time = time.time()
                self.display_fps = self.frame_count / (curr_time - self.prev_time)
                self.prev_time = curr_time
                self.frame_count = 0

            cv2.putText(frame, f"FPS: {self.display_fps:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

            # --- YOLOv8 姿勢估計核心 ---
            results = self.model.predict(source=frame, conf=0.5, classes=0, verbose=False)
            
            keypoints_detected = False
            kpt_data = None # 初始化 kpt_data
            
            for r in results:
                if hasattr(r, 'keypoints') and r.keypoints is not None:
                    kpt_data = r.keypoints.xy.cpu().numpy() # x, y coordinates for each person
                    conf_scores = r.boxes.conf.cpu().numpy() # Confidence score for each detected person
                    box_data = r.boxes.xyxy.cpu().numpy() # Bounding box for each detected person
                    class_ids = r.boxes.cls.cpu().numpy() # Class ID for each detected person (should be 0 for 'person')
                    
                    self.plot_keypoints_and_skeleton(frame, kpt_data, box_data, conf_scores, class_ids)
                    keypoints_detected = True
                    break # 通常我們只處理第一個檢測到的人
            # --- YOLOv8 姿勢估計核心結束 ---
            
            if not keypoints_detected or kpt_data is None or len(kpt_data) == 0:
                self.ui.label_warning.setText("⚠️⚠️ No person detected or keypoints not found!")
                self.label = False # 沒有檢測到人體，不執行動作判斷
            else:
                self.ui.label_warning.setText("")
                self.label = True

                # 假設只處理第一個檢測到的人
                person_keypoints = kpt_data[0] 
                
                # 從關鍵點中提取特定部位的座標
                # 這裡的索引與你的原始代碼一致，請確保它們對應 YOLOv8 的關鍵點順序
                # 例如：0-鼻子, 1-左眼, 2-右眼, 3-左耳, 4-右耳, 5-左肩, 6-右肩, 7-左肘, 8-右肘, 9-左腕, 10-右腕, 11-左臀, 12-右臀, 13-左膝, 14-右膝, 15-左踝, 16-右踝
                
                # 確保所有需要的關鍵點都存在且有效 (x, y > 0)
                required_kps_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
                if not all(person_keypoints[idx][0] > 0 and person_keypoints[idx][1] > 0 for idx in required_kps_indices if idx < len(person_keypoints)):
                    self.ui.label_warning.setText("⚠️⚠️ Some keypoints are not visible!")
                    self.label = False

                if self.label: # 如果關鍵點有效，則進行動作判斷
                    # 計算角度
                    right_elbow_angle = self.calculate_angle(
                        person_keypoints[6], person_keypoints[8], person_keypoints[10]
                    )
                    left_elbow_angle = self.calculate_angle(
                        person_keypoints[5], person_keypoints[7], person_keypoints[9]
                    )
                    both_hands_angle = self.calculate_angle(
                        person_keypoints[10], person_keypoints[0], person_keypoints[9]
                    )
                    left_body_angle = self.calculate_angle(
                        person_keypoints[9], person_keypoints[5], person_keypoints[11]
                    )
                    right_body_angle = self.calculate_angle(
                        person_keypoints[10], person_keypoints[6], person_keypoints[12]
                    )
                    left_hand_should_angle = self.calculate_angle(
                        person_keypoints[8], person_keypoints[6], person_keypoints[5]
                    )

                    left_ankle = person_keypoints[15][1]
                    left_knee = person_keypoints[13][1]
                    right_ankle = person_keypoints[16][1]
                    right_knee = person_keypoints[14][1]

                    # 動作判斷邏輯 (與你原始代碼相同)
                    # 動作一(雙手舉高舉直)
                    if (person_keypoints[10][1] < (person_keypoints[0][1] - ((person_keypoints[6][1] - person_keypoints[4][1]) / 1.1))) and \
                       (person_keypoints[9][1] < (person_keypoints[0][1] - ((person_keypoints[5][1] - person_keypoints[3][1]) / 1.1))) and self.lock1:
                        self.lock1 = False
                        active_time = time.time() - self.music_start_time
                        self.pose_timing = active_time
                        nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))
                        dif_time = active_time - nearest_beat
                        print(f"我打的節奏{active_time:.2f}s, 相差{dif_time:.2f}s, combo:{self.combo}, 加成:{self.combo_mult}")
                        t = threading.Thread(target=self.play_sound_1, args=('1',))
                        t.start()
                        tt = threading.Thread(target=self.score_cal, args=(dif_time,))
                        tt.start()
                        cool = threading.Timer(self.cool_time, self.unlock, args=('1',))
                        cool.start()
                    else:
                        if self.temp3 == '1':
                            self.stop_sound()

                    # 動作二(雙手低舉)
                    if (person_keypoints[10][1] < person_keypoints[6][1]) and \
                       (person_keypoints[9][1] < person_keypoints[5][1]) and \
                       (right_elbow_angle < 90) and (left_elbow_angle < 90) and \
                       (left_hand_should_angle > 140) and \
                       (np.abs(person_keypoints[8][0] - person_keypoints[7][0]) > (np.abs(person_keypoints[6][0] - person_keypoints[5][0]) * 2)) and self.lock2:
                        self.lock2 = False
                        active_time = time.time() - self.music_start_time
                        self.pose_timing = active_time
                        nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))
                        dif_time = active_time - nearest_beat
                        print(f"我打的節奏{active_time:.2f}s, 相差{dif_time:.2f}s, combo:{self.combo}")
                        a = threading.Thread(target=self.play_sound, args=('2',))
                        a.start()
                        aa = threading.Thread(target=self.score_cal, args=(dif_time,))
                        aa.start()
                        cool = threading.Timer(self.cool_time, self.unlock, args=('2',))
                        cool.start()

                    # 動作三:右手舉高
                    if (right_elbow_angle > 90) and (person_keypoints[10][1] < person_keypoints[1][1]) and \
                       (person_keypoints[9][1] > person_keypoints[5][1]) and (left_body_angle < 40) and self.lock3:
                        self.lock3 = False
                        active_time = time.time() - self.music_start_time
                        self.pose_timing = active_time
                        nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))
                        dif_time = active_time - nearest_beat
                        print(f"我打的節奏{active_time:.2f}s, 相差{dif_time:.2f}s, combo:{self.combo}, 加成:{self.combo_mult}")
                        b = threading.Thread(target=self.play_sound, args=('3',))
                        b.start()
                        bb = threading.Thread(target=self.score_cal, args=(dif_time,))
                        bb.start()
                        cool = threading.Timer(self.cool_time, self.unlock, args=('3',))
                        cool.start()

                    # 動作四:左手舉高
                    if (left_elbow_angle > 90) and (person_keypoints[9][1] < person_keypoints[2][1]) and \
                       (person_keypoints[10][1] > person_keypoints[6][1]) and (right_body_angle < 40) and self.lock4:
                        self.lock4 = False
                        active_time = time.time() - self.music_start_time
                        self.pose_timing = active_time
                        nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))
                        dif_time = active_time - nearest_beat
                        print(f"我打的節奏{active_time:.2f}s, 相差{dif_time:.2f}s, combo:{self.combo}, 加成:{self.combo_mult}")
                        c = threading.Thread(target=self.play_sound, args=('4',))
                        c.start()
                        cc = threading.Thread(target=self.score_cal, args=(dif_time,))
                        cc.start()
                        cool = threading.Timer(self.cool_time, self.unlock, args=('4',))
                        cool.start()

                    # 動作五:雙手張開
                    if (left_elbow_angle > 110) and (right_elbow_angle > 110) and \
                       (both_hands_angle > 130) and \
                       (right_body_angle > 70) and \
                       (left_body_angle > 70) and \
                       (np.abs(person_keypoints[10][0] - person_keypoints[9][0]) > (np.abs(person_keypoints[6][0] - person_keypoints[5][0]) * 3.2)) and self.lock5:
                        self.lock5 = False
                        active_time = time.time() - self.music_start_time
                        self.pose_timing = active_time
                        nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))
                        dif_time = active_time - nearest_beat
                        print(f"我打的節奏{active_time:.2f}s, 相差{dif_time:.2f}s, combo:{self.combo}, 加成:{self.combo_mult}")
                        d = threading.Thread(target=self.play_sound, args=('5',))
                        d.start()
                        dd = threading.Thread(target=self.score_cal, args=(dif_time,))
                        dd.start()
                        cool = threading.Timer(self.cool_time, self.unlock, args=('5',))
                        cool.start()

                    # test movements (蟋蟀音效)
                    if (left_ankle < (right_ankle - ((right_ankle - right_knee) / 4))):
                        self.aa = True
                    if self.aa:
                        if (left_ankle > (right_ankle - ((right_ankle - right_knee) / 5))):
                            e = threading.Thread(target=self.wait, args=('6',))
                            e.start()
                            self.aa = False

                    if (right_ankle < (left_ankle - ((left_ankle - left_knee) / 4))):
                        self.bb = True
                    if self.bb:
                        if (right_ankle > (left_ankle - ((left_ankle - left_knee) / 5))):
                            f = threading.Thread(target=self.wait, args=('7',))
                            f.start()
                            self.bb = False

            # 更新影像畫面 (鏡頭)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            self.qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            self.ui.labelVideo.setPixmap(QtGui.QPixmap.fromImage(self.qt_image))

    def display_frame(self, label, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        label.setPixmap(QtGui.QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.video_timer.stop()
        self.camera_timer.stop()
        if self.video_cap:
            self.video_cap.release()
        if self.camera_cap:
            self.camera_cap.release()
        print(f"總得分: {self.total_score:.2f}")
        event.accept()

if __name__ == "__main__":
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Please install the 'ultralytics' package: pip install ultralytics")
        sys.exit(1)

    # 確保 random_color.py 在同一個目錄下
    # random_color 模組內容應類似於:
    # import random
    # def get_random_color(label):
    #     random.seed(hash(label)) # 確保相同 label 得到相同顏色
    #     return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    try:
        import random_color
    except ImportError:
        logger.error("Please create a 'random_color.py' file with a 'get_random_color' function.")
        sys.exit(1)

    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
