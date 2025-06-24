import cv2
import pygame
import time
import threading
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore

class start_game:
    def __init__(self, setup_parent, ui):
        super().__init__()
        self.set = setup_parent   ###最主要的self(設定初始化的) ##也含checking_mode在self裡面了(已在setup.py指向)
        self.ui = ui       

    def start_all(self):  ##開始鍵的function
        # if self.ui.stackedWidget.currentIndex() == 1:
        #     self.mode_cap.release()
        self.set.checked_running = False
        # self.mode_cap.release()  
        self.set.mode_cap.release()
        if self.set.camera_cap:
            self.set.camera_cap.release()
        song = {'A': r"/home/nxorin/Desktop/Merry_healthy/0512/Song1/song1.wav", 'B': r"/home/nxorin/Desktop/Merry_healthy/0512/Song2/song2.wav"}
        self.set.restarted = True

        self.set.camera_cap = cv2.VideoCapture(0)
        if self.ui.stackedWidget.currentIndex() ==3:
            music_path = r"/home/nxorin/Desktop/Merry_healthy/music/Yellow.mp3"
            self.set.choose_song = ""
        if self.ui.stackedWidget.currentIndex() == 1:
            music_path = song[self.set.choose_song]        ######音樂
        
        self.set.camera_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.set.camera_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.set.camera_cap.set(cv2.CAP_PROP_FPS, 60)
        self.set.camera_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        self.start_score_timer()  ##開始計分

        if self.ui.stackedWidget.currentIndex() == 1:
            self.set.camera_timer.start(20)
        if self.ui.stackedWidget.currentIndex() == 3:
            self.set.camera_timer.stop()
            self.set.video_p2_timer.start(20)
        self.ui.label_12.setText("Loading...")

        if self.set.camera_cap:
            if self.ui.stackedWidget.currentIndex() == 3:
                self.set.video_p2_timer.timeout.disconnect()      ###換關後須重新連接才不會卡

            self.set.video_p2_timer.timeout.connect(self.set.yolo.update_camera_frame)
            QTimer.singleShot(100, lambda: threading.Thread(target=self.set.music.play_music, args=(music_path,), daemon=True).start())  #daemon=True 執行緒會在主執行緒結束時自動結束
        self.set.is_running = True

    def restart(self):
        self.set.is_running = not self.set.is_running
        self.ui.label_44.clear()
        self.set.restarted = False
        self.set.choose_song = ""
        self.ui.label_45.setText("")
        self.set.video_p2_timer.stop()
        pygame.mixer.music.stop()
        self.set.total_score = 0
        self.set.combo = 0
        self.set.checked_running  =True
        self.ui.stackedWidget.setCurrentIndex(0)  ###回到第一頁
        self.set.checked = False
        self.set.beat = 0
        for i in [self.ui.label_29, self.ui.label_30,self.ui.label_31,self.ui.label_32]:
            i.clear()
        self.ui.labelVideo.clear()
        self.ui.label_12.clear()
        self.ui.label_4.clear()
        self.ui.label_3.clear()
        self.ui.label_2.clear()
        self.ui.label.clear()
        self.set.camera_cap.release()
        cv2.destroyAllWindows()
        time.sleep(0.5)  

        threading.Thread(target=self.set.main_app.checking_mode, daemon=True).start()  ###確認所選擇的歌曲
    
    def start_score_timer(self):
        self.score_timer = QtCore.QTimer()
        self.score_timer.timeout.connect(self.set.score.show_score)
        self.score_timer.start(100)  #100毫秒更新一次

