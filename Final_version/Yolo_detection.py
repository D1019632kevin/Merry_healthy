import threading
import numpy as np
import time
import cv2
from PyQt5 import  QtGui

class yolo_pose:
    def __init__(self, parent, ui):
        super().__init__()
        self.set = parent
        self.ui = ui   

    def calculate_angle(self, a, b, c):  ##計算關節點角度的function
        a = np.array(a)  # 頭
        b = np.array(b)  # 中間點
        c = np.array(c)  # 尾
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)  # 徑轉度
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def unlock(self, number):   ##解決動作維持導致多次誤觸問題的function
        if number == '1':
            self.setting.lock1 = True
        elif number == '2':
            self.setting.lock2 = True
        elif number == '3':
            self.setting.lock3 = True
        elif number == '4':
            self.setting.lock4 = True
        elif number == '5':
            self.setting.lock5 = True

    def update_camera_frame(self):
        if not self.set.is_running or self.set.camera_cap is None:
            return
        ret, frame = self.set.camera_cap.read()
        frame = cv2.flip(frame, 1)
        if ret:
            results = self.set.model(frame, conf=0.5, classes= 0,verbose=False)
            kpt_temp = results[0].keypoints.xy 
            kpt_data = kpt_temp.cpu().numpy()  #關鍵點data

            for i in range(len(results[0].boxes)):
                body_keypoints = kpt_data[i][5:17]
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
                    self.set.label = True
                    
                    if self.set.label:
                        if(kpt_data[i][10][1] < (kpt_data[i][0][1]-((kpt_data[i][6][1]-kpt_data[i][4][1])/1.1))) & \
                            (kpt_data[i][9][1] < (kpt_data[i][0][1]-((kpt_data[i][5][1]-kpt_data[i][3][1])/1.1))) & self.set.lock1 :  # 動作一(雙手舉高舉直)
                            self.set.pose_label = '1'
                            self.set.lock1 = False
                            self.set.last_score_add_time = time.time()
                            active_time = time.time()-self.set.music_start_time
                            self.set.pose_timing = active_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            t = threading.Thread(target=self.set.music.play_sound, args=('1',))
                            t.start()
                            tt = threading.Thread(target=self.set.score.score_cal, args=(dif_time,))
                            tt.start()
                            cool = threading.Timer(self.set.cool_time, self.unlock, args=('1',))
                            cool.start()                        

                        if(kpt_data[i][10][1] < kpt_data[i][6][1]) & (kpt_data[i][9][1] < kpt_data[i][5][1]) & \
                            (right_elbow_angle < 90) & (left_elbow_angle < 90) & (left_hand_should_angle > 140) & \
                            (np.abs(kpt_data[i][8][0]-kpt_data[i][7][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*2)) & self.set.lock2:  # 動作二(雙手低舉)
                            self.set.pose_label = '2'
                            self.set.lock2 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            self.set.pose_timing = active_time
                            nearest_beat = min(self.set.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  

                            a = threading.Thread(target=self.set.music.play_sound, args=('2',))
                            a.start()
                            aa = threading.Thread(target=self.set.score.score_cal, args=(dif_time,))
                            aa.start()
                            cool = threading.Timer(self.set.cool_time, self.unlock, args=('2',))
                            cool.start()
                                                

                        if (right_elbow_angle > 90) & (kpt_data[i][10][1] < kpt_data[i][1][1]) & \
                            (kpt_data[i][9][1] > kpt_data[i][5][1]) & (left_body_angle < 40) & self.set.lock3 :  # 動作三:右手舉高
                            self.set.pose_label = '3'
                            self.set.lock3 = False
                            self.set.last_score_add_time = time.time()
                            active_time = time.time()-self.set.music_start_time
                            self.set.pose_timing = active_time
                            nearest_beat = min(self.set.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            b = threading.Thread(target=self.set.music.play_sound, args=('3',))
                            b.start()
                            bb = threading.Thread(target=self.set.score.score_cal, args=(dif_time,))
                            bb.start()
                            cool = threading.Timer(self.set.cool_time, self.unlock, args=('3',))
                            cool.start()

                        if (left_elbow_angle > 90) & (kpt_data[i][9][1] < kpt_data[i][2][1]) & \
                                (kpt_data[i][10][1] > kpt_data[i][6][1]) & (right_body_angle < 40) & self.set.lock4:  # 動作四:左手舉高
                            self.set.pose_label = '4'
                            self.set.lock4 = False
                            self.set.last_score_add_time = time.time()
                            active_time = time.time()-self.set.music_start_time
                            self.set.pose_timing = active_time
                            nearest_beat = min(self.set.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            c = threading.Thread(target=self.set.music.play_sound, args=('4',))
                            c.start()
                            cc = threading.Thread(target=self.set.score.score_cal, args=(dif_time,))
                            cc.start()
                            cool = threading.Timer(self.set.cool_time, self.unlock, args=('4',))
                            cool.start()

                        if (left_elbow_angle > 110) & (right_elbow_angle > 110) & (both_hands_angle > 130) & \
                            (right_body_angle > 70) & \
                            (left_body_angle > 70) & \
                            (np.abs(kpt_data[i][10][0]-kpt_data[i][9][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*3.2)) & self.set.lock5:  # 動作五:雙手張開
                            self.set.pose_label = '5'
                            self.set.lock5 = False
                            self.set.last_score_add_time = time.time()
                            active_time = time.time()-self.set.music_start_time
                            self.set.pose_timing = active_time
                            nearest_beat = min(self.set.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat  
                            d = threading.Thread(target=self.set.music.play_sound, args=('5',))
                            d.start()
                            dd = threading.Thread(target=self.set.score.score_cal, args=(dif_time,))
                            dd.start()
                            cool = threading.Timer(self.set.cool_time, self.unlock, args=('5',))
                            cool.start()

            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  ##更新影像畫面(鏡頭)
            h, w, ch = rgb.shape
            self.qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            if self.ui.stackedWidget.currentIndex() == 1:
                self.ui.labelVideo.setPixmap(QtGui.QPixmap.fromImage(self.qt_image))
            if self.ui.stackedWidget.currentIndex() == 3:
                self.ui.labelVideo_2.setPixmap(QtGui.QPixmap.fromImage(self.qt_image))
