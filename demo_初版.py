# cd C:\Users\user\Desktop\Merry\音樂健康
# pyuic5 -x main.ui -o ui_main.py
import sys
import cv2
import time
import librosa
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QMovie, QImage, QPixmap
from PyQt5.QtCore import QTimer
from 音樂健康.Final_version.ui_main import Ui_Game
from ultralytics import YOLO
import numpy as np
from beat_and_music import Main_music
import pygame
import threading
from threading import Timer
from pythonosc import udp_client
import time
import matplotlib.pyplot as plt
from SetUp import initial_set

class MainApp(QtWidgets.QMainWindow):
    def __init__(self): 
        super().__init__()
        self.ui = Ui_Game()  #初始化介面設定()
        self.ui.setupUi(self)
        self.model = YOLO(r'C:\Users\user\Desktop\Merry\音樂健康\weight\yolo11m-pose_fp16.engine')
        self.beat = 0.0
        self.video_cap = None
        self.camera_cap = None
        self.mode_cap = None

        self.lock1 = self.lock2 = self.lock3 = self.lock4 = self.lock5 = True

        self.gif = QMovie(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\red_fire.gif")
        self.bluegif = QMovie(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\blue_fire.gif")

        self.total_score = 0
        self.pose_image = [
            QtGui.QPixmap(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\雙手張開-4.png"),
            QtGui.QPixmap(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\舉左手-6.png"),
            QtGui.QPixmap(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\雙手半舉-5.png"),
            QtGui.QPixmap(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\舉右手-6.png")
        ]

        self.stop_score_and_combo = False
        self.aa = self.bb = False
        self.temp2 = self.temp3 = 0

        self.qt_image = None
        self.pose_label = 0
        self.choose_song = ""
        self.starting = False
        self.last_score_add = ""
        self.show_score_add = False
        self.last_score_add_time = 0

        self.beat_times = []
        self.pose_timing = 0
        self.music_start_time = 0.0
        self.beat_interval = 0.0
        self.cool_time = 0.6
        self.combo = 0
        self.combo_mult = 1.0
        self.checked = False
        self.A_timecount = self.B_timecount = None
        self.restarted = True
        self.is_running = False
        self.checked_running = True

        self.lock1 = self.lock2 = self.lock3 = self.lock4 = self.lock5 = True
        self.video_p2_timer = QtCore.QTimer()
        self.video_p2_timer.timeout.connect(self.display_score_temporarily)
        self.camera_timer = QtCore.QTimer()
        self.camera_timer.timeout.connect(self.update_camera_frame)
        self.setting = initial_set(self, self.ui)  ##設定變數 (SetUp.py)
        self.setting.setting_variable()
        self.set_music_and_beat = Main_music(self, self.ui)
       
        threading.Thread(target=self.checking_mode, daemon=True).start()  ##開始初始畫面(選擇模式)

    def calculate_angle(self, a, b, c):  ##計算關節點角度的function
        a = np.array(a)  # 頭
        b = np.array(b)  # 中間點
        c = np.array(c)  # 尾

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)  # 徑轉度
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def convert_pixmap_to_grayscale(self, pixmap):
        #轉成灰階格式
        image = pixmap.toImage().convertToFormat(QImage.Format_Grayscale8)
        return QPixmap.fromImage(image)
    
    def play_sound(self, choose_sound):  
        temp1 = choose_sound
        if temp1 == self.temp2:
            self.stop_score_and_combo = True
            return
        self.stop_score_and_combo = False
        if self.choose_song== 'A':
            sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc1.wav', '2': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc1.wav', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc2.wav', '4': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc2.wav',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc1.wav',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }
        elif self.choose_song== 'B':
            sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', '2': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav', '4': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }
        else:
            sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', '2': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav', '4': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }


        sound =pygame.mixer.Sound(sound_dict[choose_sound])
        if temp1 =="2" or temp1 =="5":
            sound.set_volume(1)
        else :
            sound.set_volume(1)    
        sound.play()
        self.temp2 = choose_sound

    # def play_sound_1(self, choose_sound):  
    #     temp1 = choose_sound
    #     if temp1 == self.temp3:
    #         self.stop_score_and_combo = True
    #         return
    #     self.stop_score_and_combo = False
    #     sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
    #                     '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
    #                     '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
    #                     '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }

    #     pygame.mixer.music.load(sound_dict[choose_sound])
    #     pygame.mixer.music.play()
    #     self.temp3 = choose_sound
        
    # def play_sound_2(self, choose_sound):  
    #     temp1 = choose_sound
    #     if temp1 == self.temp3:
    #         self.stop_score_and_combo = True
    #         return
    #     self.stop_score_and_combo = False
    #     sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
    #                     '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
    #                     '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
    #                     '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }
    #     pygame.mixer.Sound(sound_dict[choose_sound]).play()
    #     self.temp3 = choose_sound

    def check_music_end_time(self):   #檢查音樂是否結束的function
        if pygame.mixer.music.get_busy() == False and self.beat > 10 and self.ui.stackedWidget.currentIndex() == 1:
            self.ui.stackedWidget.setCurrentIndex(2)
            self.starting = False
            self.ui.label_5.setText(f"Your Score is: {self.total_score:.2f}")
        elif pygame.mixer.music.get_busy() == False and self.beat > 10 and self.ui.stackedWidget.currentIndex() == 3 : 
            self.starting = False
            self.ui.stackedWidget.setCurrentIndex(4)
            self.ui.label_25.setText(f"Your Score is: {self.total_score:.2f}")#######

    def stop_sound(self):     #終止持續音效的function(動作一)
        pygame.mixer.music.stop()
        self.temp3 = None  
    # def wait(self,num): 
    #     # time.sleep(0.2)
    #     self.play_sound_2(num)
    def start_score_timer(self):
        self.score_timer = QtCore.QTimer()
        self.score_timer.timeout.connect(self.show_score)
        self.score_timer.start(100)  #100毫秒更新一次

    def show_score(self):
        self.ui.label_10.setText(f"Score: {float(self.total_score):.2f}")
        if self.ui.stackedWidget.currentIndex() == 3:
            self.ui.label_15.setText(f"Score: {float(self.total_score):.2f}")

    def play_music(self, music_path):     ##播放背景音樂的function
        y, sr = librosa.load(music_path)           
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        self.beat_times = librosa.frames_to_time(beats, sr=sr)  ##先等librosa處理完再開始播歌
        self.beat_interval = self.beat_times[10] - self.beat_times[9]  ##計算拍子間隔
        self.ui.label_12.setText("")
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play()
        threading.Thread(target=self.play_beat, args=(self.beat_times,), daemon=True).start()
    def countdown(self):    
        sec = [3,2,1] 
        for i in sec:
            self.ui.label_beat.setText(f"{i}")
            time.sleep(1)
        self.ui.label_beat.setText("")

    def set_label_gif(self, label, movie):
        label.setMovie(movie)
        movie.start()

    def check_mode_start(self):
        self.checked = True

    def play_beat(self, beat_times):
        self.ui.label_4.clear()
        self.ui.label_3.clear()
        self.ui.label_2.clear()
        self.ui.label.clear()
        self.starting = True
        self.music_start_time = time.time()
        if self.choose_song == "B":          
            a = [4.528,5.66,
                6.792,7.925,9.057,10.189,11.321,
                12.453,13.585,14.717,15.849,16.981,
                18.113,19.245,20.377,21.509,22.642,
                23.774,24.906,26.038,27.17,28.302,29.434,
                30.566,31.698,32.83,33.962,35.094 ]
        if self.choose_song == "A":
            a=[8.727, 9.818, 10.909, 12, 13.091, 14.182, 15.273, 16.364, 17.455, 18.545,
            19.636, 20.727, 21.818, 22.909, 24, 25.091, 26.182, 27.273, 28.364, 29.455,
            30.545, 31.636, 32.727, 33.818]
        if self.choose_song == "":
            a=beat_times

        beat_count = 0
        self.ui.label_4.setPixmap(self.pose_image[3]) ##############################################
        self.ui.label_3.setPixmap(self.pose_image[2])  
        self.ui.label_2.setPixmap(self.pose_image[1])
        self.ui.label.setPixmap(self.pose_image[0])
        
        gray_image = self.convert_pixmap_to_grayscale(self.pose_image[3])
        self.ui.label_51.setPixmap(gray_image)
        gray_image = self.convert_pixmap_to_grayscale(self.pose_image[2])
        self.ui.label_50.setPixmap(gray_image)
        gray_image = self.convert_pixmap_to_grayscale(self.pose_image[1])
        self.ui.label_20.setPixmap(gray_image)
        gray_image = self.convert_pixmap_to_grayscale(self.pose_image[0])
        self.ui.label_19.setPixmap(gray_image)  
        # dots = "🔴  " * 4 
        # note =QtGui.QPixmap(r"C:\Users\user\Desktop\Merry\音樂健康\0512\rythm1.png")
        # self.ui.label_12.setPixmap(note)        
        self.ui.label_beat.setText("")
        self.ui.label_combo.setText(f"Combo ✖{self.combo}")
        self.ui.label_combo_2.setText(f"Combo ✖{self.combo}") 
        self.ui.label_combo_3.setText(f"Combo ✖{self.combo}") 

        #a = beat_times
        for i, self.beat in enumerate(a):
            if not self.restarted:
                # self.pose_gif[0].start()
                # self.pose_gif[1].start()
                # self.pose_gif[2].start()
                # self.pose_gif[3].start()

                self.ui.label_beat.clear()
                self.ui.label_29.clear()
                self.ui.label_30.clear()
                self.ui.label_31.clear()
                self.ui.label_32.clear()
                self.ui.labelVideo.clear()
                break
            # if i % 2 != 0:
            #     continue  # 每兩拍一次
            wait_time = (self.beat) - (time.time() - self.music_start_time)
                
            if wait_time > 0:  ##等到拍點
                time.sleep(wait_time)
            beat_count = (beat_count % 4) + 1  # 拍點1~4
            dots = "🔴  " * beat_count 
            for loop in [self.ui.label_29, self.ui.label_30, self.ui.label_31, self.ui.label_32, self.ui.label_33, self.ui.label_34, self.ui.label_35, self.ui.label_36
                        ,self.ui.label_42,self.ui.label_43,self.ui.label_46,self.ui.label_47,self.ui.label_55,self.ui.label_56,self.ui.label_57,self.ui.label_58]: 
                loop.setText("")

            beat_dict = {
                1:(self.ui.label_29, "🔴", self.ui.label_33, "🔴"),
                2:(self.ui.label_30, "🔴",self.ui.label_34, "🔴"),
                3:(self.ui.label_31, "🔴",self.ui.label_46, "🔵"),
                4:(self.ui.label_32, "🔴",self.ui.label_47, "🔵") }
            
            if beat_count in beat_dict:
                print(f"beat_count: {beat_count}")
                first_stage, first_icon, second_stage, second_icon = beat_dict[beat_count]
                first_stage.setText(first_icon)
                if self.ui.stackedWidget.currentIndex() == 3:
                    second_stage.setText(second_icon)

            self.ui.label_combo.setText(f"Combo ✖{self.combo}")
            if self.ui.stackedWidget.currentIndex() == 3:
                self.ui.label_combo_2.setText(f"Combo ✖{self.combo}")
                                
            if beat_count % 4 == 0:
                self.ui.label_4.setPixmap(self.pose_image[3])
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[2])
                self.ui.label_3.setPixmap(gray_image)
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[1])
                self.ui.label_2.setPixmap(gray_image)
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[0])
                self.ui.label.setPixmap(gray_image)
                if self.ui.stackedWidget.currentIndex() == 3:
                    self.ui.label_51.setPixmap(self.pose_image[3])
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[2])
                    self.ui.label_50.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[1])
                    self.ui.label_20.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[0])
                    self.ui.label_19.setPixmap(gray_image)          
            elif beat_count % 4 == 3:
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[3])
                self.ui.label_4.setPixmap(gray_image)
                self.ui.label_3.setPixmap(self.pose_image[2])
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[1])
                self.ui.label_2.setPixmap(gray_image)
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[0])
                self.ui.label.setPixmap(gray_image) 
                if self.ui.stackedWidget.currentIndex() == 3:
                    self.ui.label_50.setPixmap(self.pose_image[2])
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[3])
                    self.ui.label_51.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[1])
                    self.ui.label_20.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[0])
                    self.ui.label_19.setPixmap(gray_image)    
            elif beat_count % 4 == 2:
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[3])
                self.ui.label_4.setPixmap(gray_image)
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[2])
                self.ui.label_3.setPixmap(gray_image)
                self.ui.label_2.setPixmap(self.pose_image[1])
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[0])
                self.ui.label.setPixmap(gray_image) 
                if self.ui.stackedWidget.currentIndex() == 3:
                    self.ui.label_20.setPixmap(self.pose_image[1])
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[2])
                    self.ui.label_50.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[3])
                    self.ui.label_51.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[0])
                    self.ui.label_19.setPixmap(gray_image)   
            else:
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[3])
                self.ui.label_4.setPixmap(gray_image)
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[2])
                self.ui.label_3.setPixmap(gray_image)
                gray_image = self.convert_pixmap_to_grayscale(self.pose_image[1])
                self.ui.label_2.setPixmap(gray_image)
                self.ui.label.setPixmap(self.pose_image[0]) 
                if self.ui.stackedWidget.currentIndex() == 3:
                    self.ui.label_19.setPixmap(self.pose_image[0])
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[1])
                    self.ui.label_20.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[2])
                    self.ui.label_50.setPixmap(gray_image)
                    gray_image = self.convert_pixmap_to_grayscale(self.pose_image[3])
                    self.ui.label_51.setPixmap(gray_image)

            if abs(self.beat - self.pose_timing) > self.beat_interval*0.95 :  ##如果沒做動作(重製combo)
                self.combo = 0
                self.ui.label_combo.setText(f"Combo ✖{self.combo}")
                self.ui.label_combo_2.setText(f"Combo ✖{self.combo}")
            if self.combo < 3:   ####分數combo加成
                self.bluegif.stop()
                self.ui.label_fire.clear()
                self.ui.label_fire_2.clear()

        self.ui.label_33.setText("")
        self.ui.label_34.setText("")
        self.ui.label_35.setText("")
        self.ui.label_36.setText("")
    def start_all(self):  ##開始鍵的function
        print("cam_test start_all")
        # if self.ui.stackedWidget.currentIndex() == 1:
        #     self.mode_cap.release()
        self.checked_running = False
        # self.mode_cap.release()  
        self.mode_cap.release()
        if self.camera_cap:
            self.camera_cap.release()
        song = {'A': r"C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\song1.wav", 'B': r"C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\song2.wav"}
        self.restarted = True
        # self.video_cap = cv2.VideoCapture(r"C:\Users\user\Desktop\Merry\音樂健康\test (1).mp4")  ##影片
        self.camera_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if self.ui.stackedWidget.currentIndex() ==3:
            music_path = r"C:\Users\user\Desktop\Merry\音樂健康\music\Yellow.mp3"
            self.choose_song = ""
        if self.ui.stackedWidget.currentIndex() == 1:
            music_path = song[self.choose_song]        ######音樂
        
        self.camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.camera_cap.set(cv2.CAP_PROP_FPS, 60)
        self.camera_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.start_score_timer()
        if self.ui.stackedWidget.currentIndex() == 1:
            self.camera_timer.start(20)
        if self.ui.stackedWidget.currentIndex() == 3:
            self.camera_timer.stop()
            self.video_p2_timer.start(20)
        real_time = time.time()
        self.ui.label_12.setText("Loading...")
        # if self.ui.stackedWidget.currentIndex()== 3:
        #     # self.ui.label_18.setText("Loading...")

        if self.camera_cap :
            self.video_p2_timer.timeout.connect(self.update_camera_frame)
            if self.ui.stackedWidget.currentIndex() == 4:
                self.video_p2_timer.stop()
                self.video_p3_timer.timeout.connect(self.display_score_temporarily)
            QTimer.singleShot(100, lambda: threading.Thread(target=self.play_music, args=(music_path,), daemon=True).start())  #daemon=True 執行緒會在主執行緒結束時自動結束
        self.is_running = True
        self.ui.stopping.setText("Restart")

    def restart(self):
        self.is_running = not self.is_running
        self.ui.label_44.clear()

        self.restarted = False
        self.choose_song = ""
        self.ui.label_45.setText("")
        self.video_p2_timer.stop()
        self.video_p3_timer.stop()
        # self.ui.stopping.setText("Stop" if self.is_running else "Continue")  ##按鈕(暫停和繼續)
        pygame.mixer.music.stop()
        self.total_score = 0
        self.combo = 0
        self.checked_running  =True
        self.ui.stackedWidget.setCurrentIndex(0)
        self.checked = False
        self.beat = 0
        for i in [self.ui.label_29, self.ui.label_30,self.ui.label_31,self.ui.label_32]:
            i.clear()
        self.ui.labelVideo.clear()
        self.ui.label_12.clear()
        self.ui.label_4.clear()
        self.ui.label_3.clear()
        self.ui.label_2.clear()
        self.ui.label.clear()
        self.camera_cap.release()
        cv2.destroyAllWindows()
        time.sleep(0.5)  

        threading.Thread(target=self.checking_mode, daemon=True).start()
        
        
    def display_score_temporarily(self):  ##讓做出動作對應到的加分過0.5秒後即消失(視覺化)
        if self.show_score_add:
            self.ui.label_11.setText(self.last_score_add)
            self.ui.label_16.setText(self.last_score_add)
                
            if time.time() - self.last_score_add_time > 0.5:  ##0.5秒後加分顯示消失
                self.last_score_add = ""

    def overlay_image_alpha(self,background, overlay, x, y):
        """將 overlay（含 alpha）貼到 background 上"""
        h, w = overlay.shape[:2]

        overlay_rgb = overlay[:, :, :3]
        alpha = overlay[:, :, 3] / 255.0
        alpha = alpha[..., None]  # 調整形狀讓它可以 broadcast

        bg_crop = background[y:y+h, x:x+w]
        blended = (1 - alpha) * bg_crop + alpha * overlay_rgb
        background[y:y+h, x:x+w] = blended.astype(np.uint8)

        return background

    def checking_mode(self):
        self.mode_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)        
        self.mode_cap.set(cv2.CAP_PROP_FPS, 60)
        right_hand_x = 0
        right_hand_y = 0
        left_hand_x = 0
        left_hand_y = 0
        rock = False
        logoA= cv2.imread(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\A.png" , cv2.IMREAD_UNCHANGED)
        logoB= cv2.imread(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\B.png", cv2.IMREAD_UNCHANGED)  

        while self.checked_running:
            success, frame = self.mode_cap.read()
            if not success or frame is None or frame.shape[0] == 0 or frame.shape[1] == 0:
                continue

            frame = cv2.flip(frame, 1)
            results = self.model(frame, conf=0.5, classes=0, verbose=False)
            frame = cv2.resize(frame, (int(frame.shape[1]*1.4), int(frame.shape[0]*1.4)))

            yA = 0
            xA = int(frame.shape[1] * 0.2)
            heightA, widthA = logoA.shape[:2]
            yB = 0
            xB = int(frame.shape[1] * 0.7)
            heightB, widthB = logoB.shape[:2]
            frame = self.overlay_image_alpha(frame, logoA, xA, yA)
            frame = self.overlay_image_alpha(frame, logoB, xB, yB)
            kpt_temp = results[0].keypoints.xy
            kpt_data = kpt_temp.cpu().numpy()

            temp_area = 0
            index = -1
            for i in range(len(results[0].boxes)):
                x1, y1, x2, y2 = results[0].boxes.xyxy[i]
                area = int((x2 - x1) * (y2 - y1))
                if area > temp_area:
                    temp_area = area
                    index = i

            if index != -1 and index < len(kpt_data) :
                right_hand_x = kpt_data[index][10][0]
                right_hand_y = kpt_data[index][10][1]
                left_hand_x = kpt_data[index][9][0]
                left_hand_y = kpt_data[index][9][1]
                knee_y = kpt_data[index][13][1]
                if True: #and knee_y != 0: right_hand_y > knee_y and left_hand_y > knee_y 
                    if self.choose_song =="A" or self.choose_song == "B":
                        QtCore.QMetaObject.invokeMethod(self.ui.pushButton, "click")
                    else:
                        self.ui.label_45.setText("Please set the music")

                if right_hand_x != 0 and right_hand_y != 0 and left_hand_x != 0 and left_hand_y != 0:
                    cv2.circle(frame, (int(right_hand_x * 1.4), int(right_hand_y * 1.4)), 10, (0, 0, 255), -1)
                    cv2.circle(frame, (int(left_hand_x * 1.4), int(left_hand_y * 1.4)), 10, (0, 0, 255), -1)
                    if xA < right_hand_x * 1.4 < xA + widthA and yA < right_hand_y * 1.4 < yA + heightA:
                        if self.A_timecount is None:
                            self.A_timecount = time.time()
                        elif time.time() - self.A_timecount > 1.5:
                            if self.choose_song != "A":
                                self.ui.label_45.setText("Music A")
                                cv2.waitKey(500)
                                self.choose_song = "A"
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton_6, "click")
                    else:
                        self.A_timecount = None

                    if xB < left_hand_x * 1.4 < xB + widthB and yB < left_hand_y * 1.4 < yB + heightB:
                        if self.B_timecount is None:
                            self.B_timecount = time.time()
                        elif time.time() - self.B_timecount > 1.5:
                            if self.choose_song != "B":
                                self.ui.label_45.setText("Music B")
                                cv2.waitKey(500)
                                self.choose_song = "B"
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton_6, "click")
                    else:
                        self.B_timecount = None

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            self.ui.label_44.setPixmap(QtGui.QPixmap.fromImage(qt_image))

    def hide_score_add(self):
        self.show_score_add = False 

    def plot_keypoints(self, frame, keypoints):
        skeleton = [  ##骨架
                (5, 7), (7, 9), (6, 8), (8, 10), (5, 6), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)
            ]
        
        for pair in skeleton: #畫出YOLO骨架
            pt1, pt2 = keypoints[pair[0]], keypoints[pair[1]]
            x1, y1 = int(pt1[0]), int(pt1[1])
            x2, y2 = int(pt2[0]), int(pt2[1])
            if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        for  kpt in keypoints:
            if np.any(kpt[0]>0 or kpt[1]>0):
                cv2.circle(frame, (int(kpt[0]), int(kpt[1])), 5, (0, 0, 255), -1) #畫出關鍵點

    def score_cal(self, dif_time):
        if self.stop_score_and_combo:
            return
        best = self.beat_interval * 0.2
        nice = self.beat_interval * 0.4
        not_bad = self.beat_interval * 0.8
    
        if self.combo < 5:  #計算combo倍率
            self.combo_mult = 1.0
        elif self.combo < 9:
            self.combo_mult = 1.1
        elif self.combo < 13:
            self.combo_mult = 1.2
        else:
            self.combo_mult = 1.3

        score_add = 0

        if abs(dif_time) < best:
            score_add = 3 * self.combo_mult
            self.combo += 1
        elif abs(dif_time) <= nice:
            score_add = 2 * self.combo_mult
            self.combo += 1
        elif abs(dif_time) <= not_bad:
            score_add = 1
            self.combo = 0
        else:
            score_add = 0
            self.combo = 0
       
        self.total_score += score_add  

        if score_add > 0:
            self.last_score_add = f"+{score_add:.2f}"
            self.show_score_add = True

        QTimer.singleShot(0, self.update_fire_effect)


    def update_fire_effect(self):
        if self.combo > 5:
            self.ui.label_fire.setMovie(self.gif)
            self.gif.start()
            if self.ui.stackedWidget.currentIndex() == 3:   
                self.ui.label_fire_2.setMovie(self.gif)
                self.gif.start()
        elif self.combo > 3:
            self.ui.label_fire.setMovie(self.bluegif)
            self.bluegif.start()
            if self.ui.stackedWidget.currentIndex() == 3:   
                self.ui.label_fire_2.setMovie(self.bluegif)
                self.gif.start()
        else:
            self.gif.stop()
            self.bluegif.stop()
            self.ui.label_fire.clear()
            self.ui.label_fire_2.clear()


    def unlock(self, number):   ##解決動作維持導致多次誤觸問題的function
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
            results = self.model(frame, conf=0.5, classes= 0,verbose=False)
            kpt_temp = results[0].keypoints.xy 
            kpt_data = kpt_temp.cpu().numpy()  #關鍵點data

            for i in range(len(results[0].boxes)):
                body_keypoints = kpt_data[i][5:17]
                left_ankle = kpt_data[i][15][1]
                left_knee = kpt_data[i][13][1]
                right_ankle = kpt_data[i][16][1]
                right_knee = kpt_data[i][14][1]
                # self.plot_keypoints(frame, kpt_data[i])

                if np.any(body_keypoints == 0):                # 檢查所有關鍵點是否都偵測到condition
                    continue
                else:
                    right_elbow_angle = self.calculate_angle(  # 右軸
                        [kpt_data[i][6][0], kpt_data[i][6][1]],   
                        [kpt_data[i][8][0], kpt_data[i][8][1]],
                        [kpt_data[i][10][0], kpt_data[i][10][1]]
                    )
        
                    left_elbow_angle = self.calculate_angle(  # 左軸
                        [kpt_data[i][5][0], kpt_data[i][5][1]], 
                        [kpt_data[i][7][0], kpt_data[i][7][1]],
                        [kpt_data[i][9][0], kpt_data[i][9][1]]
                    )
                            
                    both_hands_angle = self.calculate_angle(  # 兩手
                        [kpt_data[i][10][0], kpt_data[i][10][1]], 
                        [kpt_data[i][0][0], kpt_data[i][0][1]],
                        [kpt_data[i][9][0], kpt_data[i][9][1]]
                    )
                    left_body_angle = self.calculate_angle(  # 右身
                        [kpt_data[i][9][0], kpt_data[i][9][1]],
                        [kpt_data[i][5][0], kpt_data[i][5][1]],
                        [kpt_data[i][11][0], kpt_data[i][11][1]]
                    )
                    right_body_angle = self.calculate_angle(  # 左身
                        [kpt_data[i][10][0], kpt_data[i][10][1]],
                        [kpt_data[i][6][0], kpt_data[i][6][1]],
                        [kpt_data[i][12][0], kpt_data[i][12][1]]
                    )
                    left_hand_should_angle = self.calculate_angle(  # 左手肘
                        [kpt_data[i][8][0], kpt_data[i][8][1]],
                        [kpt_data[i][6][0], kpt_data[i][6][1]],
                        [kpt_data[i][5][0], kpt_data[i][5][1]]
                    )
                    self.label = True
                    
                    if self.label:
                        if(kpt_data[i][10][1] < (kpt_data[i][0][1]-((kpt_data[i][6][1]-kpt_data[i][4][1])/1.1))) & \
                            (kpt_data[i][9][1] < (kpt_data[i][0][1]-((kpt_data[i][5][1]-kpt_data[i][3][1])/1.1))) & self.lock1 and not self.starting:                          
                            QtCore.QMetaObject.invokeMethod(self.ui.pushButton_7, "click")

                        if(kpt_data[i][10][1] < (kpt_data[i][0][1]-((kpt_data[i][6][1]-kpt_data[i][4][1])/1.1))) & \
                            (kpt_data[i][9][1] < (kpt_data[i][0][1]-((kpt_data[i][5][1]-kpt_data[i][3][1])/1.1))) & self.lock1 :  # 動作一(雙手舉高舉直)
                            self.pose_label = '1'
                            self.lock1 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            self.pose_timing = active_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            t = threading.Thread(target=self.play_sound, args=('1',))
                            t.start()
                            tt = threading.Thread(target=self.score_cal, args=(dif_time,))
                            tt.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('1',))
                            cool.start()                        

                        if(kpt_data[i][10][1] < kpt_data[i][6][1]) & (kpt_data[i][9][1] < kpt_data[i][5][1]) & \
                            (right_elbow_angle < 90) & (left_elbow_angle < 90) & (left_hand_should_angle > 140) & \
                            (np.abs(kpt_data[i][8][0]-kpt_data[i][7][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*2)) & self.lock2:  # 動作二(雙手低舉)
                            self.pose_label = '2'
                            self.lock2 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            self.pose_timing = active_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  

                            a = threading.Thread(target=self.play_sound, args=('2',))
                            a.start()
                            aa = threading.Thread(target=self.score_cal, args=(dif_time,))
                            aa.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('2',))
                            cool.start()
                            # self.play_sound('2')
                            # CLIENT.send_message("/player3", [2]) 
                                                

                        if (right_elbow_angle > 90) & (kpt_data[i][10][1] < kpt_data[i][1][1]) & \
                            (kpt_data[i][9][1] > kpt_data[i][5][1]) & (left_body_angle < 40) & self.lock3 :  # 動作三:右手舉高
                            self.pose_label = '3'
                            self.lock3 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            self.pose_timing = active_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            b = threading.Thread(target=self.play_sound, args=('3',))
                            b.start()
                            bb = threading.Thread(target=self.score_cal, args=(dif_time,))
                            bb.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('3',))
                            cool.start()

                        if (left_elbow_angle > 90) & (kpt_data[i][9][1] < kpt_data[i][2][1]) & \
                                (kpt_data[i][10][1] > kpt_data[i][6][1]) & (right_body_angle < 40) & self.lock4:  # 動作四:左手舉高
                            print("右手")
                            self.pose_label = '4'
                            self.lock4 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            self.pose_timing = active_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            c = threading.Thread(target=self.play_sound, args=('4',))
                            c.start()
                            cc = threading.Thread(target=self.score_cal, args=(dif_time,))
                            cc.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('4',))
                            cool.start()

                        if (left_elbow_angle > 110) & (right_elbow_angle > 110) & (both_hands_angle > 130) & \
                            (right_body_angle > 70) & \
                            (left_body_angle > 70) & \
                            (np.abs(kpt_data[i][10][0]-kpt_data[i][9][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*3.2)) & self.lock5:  # 動作五:雙手張開
                            self.pose_label = '5'
                            self.lock5 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            self.pose_timing = active_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            d = threading.Thread(target=self.play_sound, args=('5',))
                            d.start()
                            dd = threading.Thread(target=self.score_cal, args=(dif_time,))
                            dd.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('5',))
                            cool.start()

            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  ##更新影像畫面(鏡頭)
            h, w, ch = rgb.shape
            self.qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            if self.ui.stackedWidget.currentIndex() == 1:
                self.ui.labelVideo.setPixmap(QtGui.QPixmap.fromImage(self.qt_image))
            if self.ui.stackedWidget.currentIndex() == 3:
                self.ui.labelVideo_2.setPixmap(QtGui.QPixmap.fromImage(self.qt_image))

    def back_to_page1(self):
        if self.ui.stackedWidget.currentIndex() == 2:
            self.ui.stackedWidget.setCurrentIndex(3)
        if self.ui.stackedWidget.currentIndex() == 4:
            self.ui.stackedWidget.setCurrentIndex(5)
        self.total_score = 0
        self.beat = 0
        if self.ui.pushButton_7.isChecked():
            
            self.start_all()
        
    def to_page_2(self): 
        #self.checked_running = False
        #self.mode_cap.release()  
        self.ui.stackedWidget.setCurrentIndex(1)
        self.total_score = 0
        self.beat = 0

    def closeEvent(self, event):
        self.camera_timer.stop()
        if self.video_cap:
            self.video_cap.release()
        if self.camera_cap:
            self.camera_cap.release()

        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
