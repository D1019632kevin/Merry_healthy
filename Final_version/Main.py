# cd C:\Users\user\Desktop\Merry\音樂健康
# pyuic5 -x main.ui -o ui_main.py
import os
import sys
import cv2
import time
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QLibraryInfo
from ui_main import Ui_Game
import numpy as np
import pygame
import threading
import time
from SetUp import initial_set
import onnxruntime as ort
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"]=QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)
session_options = ort.SessionOptions()
session_options.log_severity_level =1
class MainApp(QtWidgets.QMainWindow):
    def __init__(self): 
        super().__init__()
        self.ui = Ui_Game()  #初始化介面設定()
        self.ui.setupUi(self)       
        self.setting = initial_set(self, self.ui)  ##設定變數 (SetUp.py)

        threading.Thread(target=self.checking_mode, daemon=True).start()  ##開始初始畫面(選擇模式)


    def check_music_end_time(self):   #檢查音樂是否結束的function
        if pygame.mixer.music.get_busy() == False and self.setting.beat > 10 and self.ui.stackedWidget.currentIndex() == 1:
            self.ui.stackedWidget.setCurrentIndex(2)
            self.setting.starting = False
            self.ui.label_5.setText(f"Your Score is: {self.setting.total_score:.2f}")
        elif pygame.mixer.music.get_busy() == False and self.setting.beat > 10 and self.ui.stackedWidget.currentIndex() == 3 : 
            self.setting.starting = False
            self.ui.stackedWidget.setCurrentIndex(4)
            self.ui.label_25.setText(f"Your Score is: {self.setting.total_score:.2f}")#######


    def check_mode_start(self):
        self.setting.checked = True
            
    def display_score_temporarily(self):  ##讓做出動作對應到的加分過0.5秒後即消失(視覺化)
        if self.setting.show_score_add:
            self.ui.label_11.setText(self.setting.last_score_add)
            self.ui.label_35.setText(self.setting.last_score_add)
                
            if time.time() - self.setting.last_score_add_time > 0.5:  ##0.5秒後加分顯示消失
                self.setting.last_score_add = ""

    def overlay_image_alpha(self,background, overlay, x, y):
        h, w = overlay.shape[:2]

        overlay_rgb = overlay[:, :, :3]
        alpha = overlay[:, :, 3] / 255.0
        alpha = alpha[..., None]  # 調整形狀讓它可以 broadcast

        bg_crop = background[y:y+h, x:x+w]
        blended = (1 - alpha) * bg_crop + alpha * overlay_rgb
        background[y:y+h, x:x+w] = blended.astype(np.uint8)

        return background

    def checking_mode(self):
        self.setting.mode_cap = cv2.VideoCapture(0)        
        self.setting.mode_cap.set(cv2.CAP_PROP_FPS, 60)
        right_hand_x = 0
        right_hand_y = 0
        left_hand_x = 0
        left_hand_y = 0
        logoA= cv2.imread(r"/home/nxorin/Desktop/Merry_healthy/gif素材/A.png" , cv2.IMREAD_UNCHANGED)
        logoB= cv2.imread(r"/home/nxorin/Desktop/Merry_healthy/gif素材/B.png", cv2.IMREAD_UNCHANGED)  

        while self.setting.checked_running:
            success, frame = self.setting.mode_cap.read()
            if not success or frame is None or frame.shape[0] == 0 or frame.shape[1] == 0:
                continue

            frame = cv2.flip(frame, 1)
            results = self.setting.model(frame, conf=0.5, classes=0, verbose=False)
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
                if True: #and knee_y != 0: right_hand_y > knee_y and left_hand_y > knee_y 
                    if self.setting.choose_song =="A" or self.setting.choose_song == "B":
                        continue
                    else:
                        self.ui.label_45.setText("Please set the music")

                if right_hand_x != 0 and right_hand_y != 0 and left_hand_x != 0 and left_hand_y != 0:
                    cv2.circle(frame, (int(right_hand_x * 1.4), int(right_hand_y * 1.4)), 10, (0, 0, 255), -1)
                    cv2.circle(frame, (int(left_hand_x * 1.4), int(left_hand_y * 1.4)), 10, (0, 0, 255), -1)
                    if xA < right_hand_x * 1.4 < xA + widthA and yA < right_hand_y * 1.4 < yA + heightA:
                        if self.setting.A_timecount is None:
                            self.setting.A_timecount = time.time()
                        elif time.time() - self.setting.A_timecount > 1.5:
                            if self.setting.choose_song != "A":
                                self.ui.label_45.setText("Music A")
                                cv2.waitKey(500)
                                self.setting.choose_song = "A"
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton_6, "click")
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton, "click")
                    else:
                        self.setting.A_timecount = None

                    if xB < left_hand_x * 1.4 < xB + widthB and yB < left_hand_y * 1.4 < yB + heightB:
                        if self.setting.B_timecount is None:
                            self.setting.B_timecount = time.time()
                        elif time.time() - self.setting.B_timecount > 1.5:
                            if self.setting.choose_song != "B":
                                self.ui.label_45.setText("Music B")
                                cv2.waitKey(500)
                                self.setting.choose_song = "B"
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton_6, "click")
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton, "click")
                    else:
                        self.setting.B_timecount = None

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            self.ui.label_44.setPixmap(QtGui.QPixmap.fromImage(qt_image))

    def update_fire_effect(self):
        if self.setting.combo > 5:
            self.ui.label_fire.setMovie(self.setting.gif)
            self.setting.gif.start()
            if self.ui.stackedWidget.currentIndex() == 3:   
                self.ui.label_fire_2.setMovie(self.setting.gif)
                self.setting.gif.start()
        elif self.setting.combo > 3:
            self.ui.label_fire.setMovie(self.setting.bluegif)
            self.setting.bluegif.start()
            if self.ui.stackedWidget.currentIndex() == 3:   
                self.ui.label_fire_2.setMovie(self.setting.bluegif)
                self.setting.gif.start()
        else:
            self.setting.gif.stop()
            self.setting.bluegif.stop()
            self.ui.label_fire.clear()
            self.ui.label_fire_2.clear()

    def back_to_page1(self):
        if self.ui.stackedWidget.currentIndex() == 2:
            self.ui.stackedWidget.setCurrentIndex(3)
        if self.ui.stackedWidget.currentIndex() == 4:
            self.ui.stackedWidget.setCurrentIndex(5)
        self.total_score = 0
        self.setting.beat = 0  
        
    def to_page_2(self): 
        self.ui.stackedWidget.setCurrentIndex(1)
        self.total_score = 0
        self.setting.beat = 0

    def closeEvent(self, event):
        self.setting.camera_timer.stop()
        if self.setting.video_cap:
            self.setting.video_cap.release()
        if self.setting.camera_cap:
            self.setting.camera_cap.release()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
