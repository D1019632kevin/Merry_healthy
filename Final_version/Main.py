# cd C:\Users\user\Desktop\Merry\音樂健康
# pyuic5 -x main.ui -o ui_main.py
'''''''主程式(執行此程式即可開始)'''''''''
import sys      
import cv2  
import time
from PyQt5 import QtWidgets, QtGui, QtCore
from ui_main import Ui_Game
import numpy as np
import pygame
import threading
import time
from SetUp import initial_set  ##匯入參數初始化設定的python檔

class MainApp(QtWidgets.QMainWindow):
    def __init__(self): 
        super().__init__()
        self.ui = Ui_Game()  #初始化介面設定()
        self.ui.setupUi(self)       
        self.setting = initial_set(self, self.ui)  ##設定變數 (SetUp.py)

        threading.Thread(target=self.checking_mode, daemon=True).start()  ##開始初始畫面(選擇模式)

    def check_music_end_time(self):   #檢查音樂跟遊戲是否結束的function(結束就翻下一頁)
        if pygame.mixer.music.get_busy() == False and self.setting.beat > 10 and self.ui.stackedWidget.currentIndex() == 1:  ##若音樂停止播放且拍點大於10且目前在第一頁
            self.ui.stackedWidget.setCurrentIndex(2)  ##翻到下一頁(顯示分數)
            self.setting.starting = False
            self.ui.label_5.setText(f"Your Score is: {self.setting.total_score:.2f}")
        elif pygame.mixer.music.get_busy() == False and self.setting.beat > 10 and self.ui.stackedWidget.currentIndex() == 3 : ##若音樂停止播放且拍點大於10且目前在第三頁
            self.setting.starting = False     
            self.ui.stackedWidget.setCurrentIndex(4)  ##翻到下一頁(顯示分數)
            self.ui.label_25.setText(f"Your Score is: {self.setting.total_score:.2f}")

    # def check_mode_start(self):
    #     self.setting.checked = True

    def overlay_image_alpha(self,background, overlay, x, y):  ###將a、b模式的圖樣去背後顯示在畫面中
        h, w = overlay.shape[:2]

        overlay_rgb = overlay[:, :, :3]
        alpha = overlay[:, :, 3] / 255.0
        alpha = alpha[..., None]  

        bg_crop = background[y:y+h, x:x+w]
        blended = (1 - alpha) * bg_crop + alpha * overlay_rgb
        background[y:y+h, x:x+w] = blended.astype(np.uint8)

        return background

    def checking_mode(self):    ##初始畫面(選擇模式畫面)
        self.setting.mode_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  ##開啟鏡頭連線    
        self.setting.mode_cap.set(cv2.CAP_PROP_FPS, 60)
        right_hand_x = 0
        right_hand_y = 0
        left_hand_x = 0
        left_hand_y = 0
        logoA= cv2.imread(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\A.png" , cv2.IMREAD_UNCHANGED)   ###a、b模式的素材
        logoB= cv2.imread(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\B.png", cv2.IMREAD_UNCHANGED)  

        while self.setting.checked_running:  ##確認正在選擇模式畫面中(start_all後就改完False)
            success, frame = self.setting.mode_cap.read() ##讀取畫面
            if not success or frame is None or frame.shape[0] == 0 or frame.shape[1] == 0:  ##畫面讀取失敗
                continue

            frame = cv2.flip(frame, 1)  ##反轉畫面
            results = self.setting.model(frame, conf=0.5, classes=0, verbose=False)  ##模型偵測存在results中
            frame = cv2.resize(frame, (int(frame.shape[1]*1.4), int(frame.shape[0]*1.4)))  ##縮小畫面

            yA = 0
            xA = int(frame.shape[1] * 0.2)
            heightA, widthA = logoA.shape[:2]
            yB = 0
            xB = int(frame.shape[1] * 0.7)
            heightB, widthB = logoB.shape[:2]
            frame = self.overlay_image_alpha(frame, logoA, xA, yA)  ##將a、b模式的圖樣去背後顯示在畫面中
            frame = self.overlay_image_alpha(frame, logoB, xB, yB)
            kpt_temp = results[0].keypoints.xy  ##偵測到的關鍵點
            kpt_data = kpt_temp.cpu().numpy()  ##需要先推到cpu做推理(再轉np)

            temp_area = 0
            index = -1  
            for i in range(len(results[0].boxes)):
                x1, y1, x2, y2 = results[0].boxes.xyxy[i]  ##偵測到的人體區域
                area = int((x2 - x1) * (y2 - y1))
                if area > temp_area:  ##找出面積最大的人體(畫面中只有一個人會顯示手部關鍵點)
                    temp_area = area
                    index = i

            if index != -1 and index < len(kpt_data) :  #index=-1代表沒有偵測人體(因為index一直沒被取代)
                right_hand_x = kpt_data[index][10][0]
                right_hand_y = kpt_data[index][10][1]
                left_hand_x = kpt_data[index][9][0]
                left_hand_y = kpt_data[index][9][1]
                if self.setting.choose_song =="A" or self.setting.choose_song == "B":  ##若已經選擇模式
                    continue
                else:
                    self.ui.label_45.setText("Please set the music")

                if right_hand_x != 0 and right_hand_y != 0 and left_hand_x != 0 and left_hand_y != 0:  ##手都有被偵測到才執行
                    cv2.circle(frame, (int(right_hand_x * 1.4), int(right_hand_y * 1.4)), 10, (0, 0, 255), -1)  ##在畫面上顯示手的關鍵點
                    cv2.circle(frame, (int(left_hand_x * 1.4), int(left_hand_y * 1.4)), 10, (0, 0, 255), -1)
                    if xA < right_hand_x * 1.4 < xA + widthA and yA < right_hand_y * 1.4 < yA + heightA:  ##判斷手是否在a、b模式的圖樣上
                        if self.setting.A_timecount is None:
                            self.setting.A_timecount = time.time()
                        elif time.time() - self.setting.A_timecount > 1.5:  ##判斷關鍵點是否停留超過1.5秒
                            if self.setting.choose_song != "A":
                                self.ui.label_45.setText("Music A")
                                cv2.waitKey(200)
                                self.setting.choose_song = "A"
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton_6, "click")  ##直接觸發按鈕
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton, "click")
                    else:
                        self.setting.A_timecount = None  ##沒停留超過1.5秒就重製計時

                    if xB < left_hand_x * 1.4 < xB + widthB and yB < left_hand_y * 1.4 < yB + heightB:  ##判斷手是否在a、b模式的圖樣上
                        if self.setting.B_timecount is None:
                            self.setting.B_timecount = time.time()
                        elif time.time() - self.setting.B_timecount > 1.5:  ##判斷關鍵點是否停留超過1.5秒
                            if self.setting.choose_song != "B":
                                self.ui.label_45.setText("Music B")
                                cv2.waitKey(200)
                                self.setting.choose_song = "B"
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton_6, "click")   ##直接觸發按鈕
                                QtCore.QMetaObject.invokeMethod(self.ui.pushButton, "click")
                    else:
                        self.setting.B_timecount = None  ##沒停留超過1.5秒就重製計時

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  ##更新介面上的畫面
            h, w, ch = rgb.shape
            qt_image = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
            self.ui.label_44.setPixmap(QtGui.QPixmap.fromImage(qt_image))

    def update_fire_effect(self):  ##更新火焰特效
        if self.setting.combo > 5:  ##判斷combo是否大於5
            self.ui.label_fire.setMovie(self.setting.gif)
            self.setting.gif.start()
            if self.ui.stackedWidget.currentIndex() == 3:    ##判斷目前在第三頁(更新另外一頁的Label) 
                self.ui.label_fire_2.setMovie(self.setting.gif)
                self.setting.gif.start()
        elif self.setting.combo > 3:  ##判斷combo是否大於3
            self.ui.label_fire.setMovie(self.setting.bluegif)
            self.setting.bluegif.start()
            if self.ui.stackedWidget.currentIndex() == 3:  ##判斷目前在第三頁(更新另外一頁的Label) 
                self.ui.label_fire_2.setMovie(self.setting.bluegif)
                self.setting.gif.start()
        else:  ##判斷combo是否小於等於3(則停止火焰特效)
            self.setting.gif.stop()
            self.setting.bluegif.stop()
            self.ui.label_fire.clear()
            self.ui.label_fire_2.clear()

    def to_next_page(self):  ##跳轉下一頁
        if self.ui.stackedWidget.currentIndex() == 0:
            self.ui.stackedWidget.setCurrentIndex(1)
        if self.ui.stackedWidget.currentIndex() == 2:
            self.ui.stackedWidget.setCurrentIndex(3)
        if self.ui.stackedWidget.currentIndex() == 4:
            self.ui.stackedWidget.setCurrentIndex(5)
        self.total_score = 0  ##分數跟beat重製
        self.setting.beat = 0  
        
    def closeEvent(self, event):  ##關閉視窗的function(右上角叉叉)
        self.setting.camera_timer.stop()
        if self.setting.video_cap:
            self.setting.video_cap.release()
        if self.setting.camera_cap:
            self.setting.camera_cap.release()
        event.accept()

if __name__ == "__main__":   ##呼叫主程式
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
