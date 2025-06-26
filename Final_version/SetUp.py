
from ultralytics import YOLO
from PyQt5.QtGui import QMovie
from PyQt5 import  QtGui, QtCore
import pygame
from start import start_game   ###導入python檔
from Yolo_detection import yolo_pose
from score import show_score
from beat_and_music import Main_music

'''''''參數設定的python檔,不須執行'''''''''

class initial_set:
    def __init__(self, parent,ui):
        self.main_app = parent  #把Main.py的class傳進來
        self.ui = ui  #把介面傳進來
        pygame.mixer.init()  #pygame initial
        self.start = start_game(self, self.ui)   ##將把SetUp跟Main的self都傳入對應程式碼當中
        self.yolo = yolo_pose(self, self.ui)
        self.score = show_score(self, self.ui)
        self.music = Main_music(self, self.ui)

        self.model = YOLO(r'C:\Users\user\Desktop\Merry\音樂健康\weight\yolo11m-pose_fp16.engine')  ##YOLO模型檔
        self.beat = 0.0
        self.video_cap = None
        self.camera_cap = None
        self.mode_cap = None
        self.test = ""

        self.lock1 = self.lock2 = self.lock3 = self.lock4 = self.lock5 = True  ##用在避免一個動作持續觸發

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
        # self.checked = False
        self.A_timecount = self.B_timecount = None
        self.restarted = True
        self.is_running = False
        self.checked_running = True
        self.ui.stopping.setText("Restart")

        for i in [self.ui.pushButton, self.ui.pushButton_4, self.ui.pushButton_9]:  ##開始按鈕設定
            i.clicked.connect(self.start.start_all)

        for i in [self.ui.pushButton_5, self.ui.stopping, self.ui.pushButton_10, self.ui.stopping_2, self.ui.pushButton_12]:  ##重新開始按鈕設定
            i.clicked.connect(self.start.restart)

        for i in [self.ui.pushButton_2]:
            i.clicked.connect(self.main_app.to_next_page)

        self.ui.pushButton_6.clicked.connect(self.main_app.to_next_page)

        for i in [self.ui.pushButton_8, self.ui.pushButton_3]:
            i.clicked.connect(self.main_app.close)

        self.camera_timer = QtCore.QTimer()   ##定時器
        self.camera_timer.timeout.connect(self.yolo.update_camera_frame)  ##後面程式會觸發(更新畫面和模型辨識)

        self.check_music_end = QtCore.QTimer()  ##定時器
        self.check_music_end.timeout.connect(self.main_app.check_music_end_time)  
        self.check_music_end.start(500)  ##o.5秒執行一次check_music_end_time(檢查音樂結束時間)

        self.video_p2_timer = QtCore.QTimer()  
        self.video_p2_timer.timeout.connect(self.score.display_score_temporarily)  ##讓做出動作對應到的加分過0.5秒後即消失
        self.video_p2_timer.start(20)

        



        
