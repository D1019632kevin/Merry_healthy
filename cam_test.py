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
#import pydirectinput #windows only
import pygame
import threading
from threading import Timer
from pythonosc import udp_client
import time
import matplotlib.pyplot as plt

pygame.mixer.init()
class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.total_score = 0
        self.prev_time = 0
        self.sound_dict = {}

        self.aa= self.bb= False
        self.temp2=self.temp3 = 0

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


        self.model = YOLO(r'weight/yolo11s-pose_rknn_model')
        self.video_cap = self.camera_cap = None
        self.lock1 = self.lock2 = self.lock3 = self.lock4= self.lock5=True

        self.is_running = False
        self.ui.stopping.setText("stop")

        self.video_timer = QtCore.QTimer()
        self.video_timer.timeout.connect(self.update_video_frame)

        self.camera_timer = QtCore.QTimer()
        self.camera_timer.timeout.connect(self.update_camera_frame)

        self.ui.pushButton.clicked.connect(self.start_all)
        self.ui.stopping.clicked.connect(self.toggle_playback)
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

    def stop_sound(self):     #終止持續音效的function(動作一)
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
    def play_music(self, music_path):     ##播放背景音樂的function
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
            if abs(self.beat - self.pose_timing) > self.beat_interval*0.9 :  ##如果沒做動作
                self.combo = 0
                self.ui.label_combo.setText(f"Combo ✖{self.combo}")
            if self.combo < 3:   ####分數combo加成
                self.bluegif.stop()
                self.ui.label_fire.clear()

    def start_all(self):
        self.video_cap = cv2.VideoCapture(r"/home/orangepi/Desktop/Merry_healthy/test (1).mp4")
        music_path = r"/home/orangepi/Desktop/Merry_healthy/song_low.mp3"
        threading.Thread(target=self.play_music(music_path)).start()  #daemon=True 執行緒會在主執行緒結束時自動結束
        self.camera_cap = cv2.VideoCapture(0) #ubuntu no use cv2.CAP_DSHOW
        self.camera_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.camera_cap.set(cv2.CAP_PROP_FPS, 35)
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
    def plot_keypoints(self, frame, keypoints):
        for  kpt in keypoints:
            if np.any(kpt[0]>0 or kpt[1]>0):
                cv2.circle(frame, (int(kpt[0]), int(kpt[1])), 5, (0, 0, 255), -1) #畫出關鍵點

        skeleton = [  ##骨架
                (5, 7), (7, 9), (6, 8), (8, 10), (5, 6), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)
            ]
        
        for pair in skeleton: #畫出YOLO骨架
            pt1, pt2 = keypoints[pair[0]], keypoints[pair[1]]
            x1, y1 = int(pt1[0]), int(pt1[1])
            x2, y2 = int(pt2[0]), int(pt2[1])
            if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    def score_cal(self, dif_time):
        best = self.beat_interval*0.2  ##最佳拍點  1
        nice = self.beat_interval*0.4  #2
        not_bad = self.beat_interval*0.8#3
        print(best, nice, not_bad)

        if self.combo < 5:   ####分數combo加成
            self.combo_mult = 1.0
        elif self.combo < 9:
            self.combo_mult = 1.1
        elif self.combo < 13:
            self.combo_mult = 1.25
        else:
            self.combo_mult = 1.5 

        if abs(dif_time) < best:         ##best跟nice才有combo加成(self.combo_mult)
            self.total_score += 3*self.combo_mult
            self.combo += 1
        elif abs(dif_time) <= nice:
            self.total_score += 2 *self.combo_mult
            self.combo += 1
        elif abs(dif_time) <= not_bad:
            self.total_score += 1
            self.combo = 0
        else:
            self.combo = 0
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
            self.frame_count += 1
            
            if self.frame_count >= 5:       # 五幀更新一次FPS
                curr_time = time.time()
                self.display_fps = self.frame_count / (curr_time - self.prev_time)
                self.prev_time = curr_time
                self.frame_count = 0    

            cv2.putText(frame, f"FPS: {self.display_fps:.2f}", (10, 30),   #FPS 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

            results = self.model(frame, conf=0.5, classes= 0,verbose=False)
            kpt_temp = results[0].keypoints.xy 
            kpt_data = kpt_temp.cpu().numpy()  #關鍵點data

            for i in range(len(results[0].boxes)):
                body_keypoints = kpt_data[i][5:17]
                left_ankle = kpt_data[i][15][1]
                left_knee = kpt_data[i][13][1]
                right_ankle = kpt_data[i][16][1]
                right_knee = kpt_data[i][14][1]
                self.plot_keypoints(frame, kpt_data[i])

                if np.any(body_keypoints == 0):                # 檢查所有關鍵點是否都偵測到condition
                    self.ui.label_warning.setText("⚠️⚠️")
                    continue
                else:
                    self.ui.label_warning.setText("")
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
                    
                # if self.combo > 5 & self.reset_blue_fire:
                #     self.reset_blue_fire = False
                #     self.ui.label_fire.setMovie(self.bluegif)
                #     self.bluegif.start()
                #     self.ui.label_combo.setText(f"Combo ✖{self.combo}")

                # elif self.combo > 3 & self.reset_fire:
                #     self.reset_fire = False
                #     self.ui.label_fire.setMovie(self.gif)
                #     self.gif.start()
                #     self.ui.label_combo.setText(f"Combo ✖{self.combo}")

                # else:
                #     self.reset_blue_fire = True
                #     self.reset_fire = True
                #     self.gif.stop()
                #     self.bluegif.stop()
                #     self.ui.label_fire.clear()
                #     self.ui.label_combo.setText("") 

                    if self.label:
                        if(kpt_data[i][10][1] < (kpt_data[i][0][1]-((kpt_data[i][6][1]-kpt_data[i][4][1])/1.1))) & \
                            (kpt_data[i][9][1] < (kpt_data[i][0][1]-((kpt_data[i][5][1]-kpt_data[i][3][1])/1.1))) & self.lock1:  # 動作一(雙手舉高舉直)
                            self.lock1 = False
                            active_time = time.time()-self.music_start_time
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


                            # self.play_sound('1')
                            # CLIENT.send_message("/player3", [1])
                        else:
                            if self.temp3 == '1':
                                self.stop_sound()
                        

                        if(kpt_data[i][10][1] < kpt_data[i][6][1]) & (kpt_data[i][9][1] < kpt_data[i][5][1]) & \
                            (right_elbow_angle < 90) & (left_elbow_angle < 90) & (left_hand_should_angle > 140) & \
                            (np.abs(kpt_data[i][8][0]-kpt_data[i][7][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*2)) & self.lock2:  # 動作二(雙手低舉)
                            self.lock2 = False
                            active_time = time.time()-self.music_start_time
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
                            # self.play_sound('2')
                            # CLIENT.send_message("/player3", [2]) 
                                                

                        if (right_elbow_angle > 90) & (kpt_data[i][10][1] < kpt_data[i][1][1]) & \
                            (kpt_data[i][9][1] > kpt_data[i][5][1]) & (left_body_angle < 40) & self.lock3:  # 動作三:右手舉高
                            self.lock3 = False
                            active_time = time.time()-self.music_start_time
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
                            # self.play_sound('3')
                            # CLIENT.send_message("/player3", [3]) 
                            

                        if (left_elbow_angle > 90) & (kpt_data[i][9][1] < kpt_data[i][2][1]) & \
                                (kpt_data[i][10][1] > kpt_data[i][6][1]) & (right_body_angle < 40) & self.lock4:  # 動作四:左手舉高
                            self.lock4 = False
                            active_time = time.time()-self.music_start_time
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
                            # self.play_sound('4')
                            # CLIENT.send_message("/player3", [4]) 

                        if (left_elbow_angle > 110) & (right_elbow_angle > 110) & (both_hands_angle > 130) & \
                            (right_body_angle > 70) & \
                            (left_body_angle > 70) & \
                            (np.abs(kpt_data[i][10][0]-kpt_data[i][9][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*3.2)) & self.lock5:  # 動作五:雙手張開
                            self.lock5 = False
                            active_time = time.time()-self.music_start_time
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
                            # self.play_sound('5')
                            # CLIENT.send_message("/player3", [5]) 

                        if (left_ankle < (right_ankle - ((right_ankle-right_knee)/4))):  ##test
                            self.aa= True
                            # CLIENT.send_message("/player3", [6]) 
                        if self.aa:
                            if (left_ankle > (right_ankle - ((right_ankle-right_knee)/5))):
                                e = threading.Thread(target=self.wait,args=('6'))
                                e.start()

                                self.aa = False
                                # self.play_sound('6')
                                # pydirectinput.keyDown('0')
                                # pydirectinput.keyUp('0')

                        if (right_ankle < (left_ankle - ((left_ankle-left_knee)/4))):  ##test
                            self.bb = True
                            # CLIENT.send_message("/player3", [7]) 
                        if self.bb:
                            if (right_ankle > (left_ankle - ((left_ankle-left_knee)/5))): 
                                f = threading.Thread(target=self.wait,args=('7'))
                                f.start()
                                
                                self.bb = False
                                # pydirectinput.keyDown('1')
                                # pydirectinput.keyUp('1')

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  ##更新影像畫面(鏡頭)
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
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
