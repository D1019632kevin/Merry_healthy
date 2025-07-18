from ultralytics import YOLO
import numpy as np
import cv2
import pygame
import threading
from pythonosc import udp_client, dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import time
import librosa
# from ffpyplayer.player import MediaPlayer

# IP = "192.168.0.90" 
IP = "10.75.201.135"
RECEIVE_IP = "0.0.0.0"
PORT1 = 7676
PORT2 = 7675
CLIENT = udp_client.SimpleUDPClient(IP, PORT2)
DISP = dispatcher.Dispatcher()

pygame.mixer.init()
class Interface:
    def __init__(self, model, video_path, label):

        self.model = model
        self.video_path = video_path
        self.sound_dict = {}
        self.cool_time = 0.2
        self.change_flag= False
        self.music_start_time = 0
        self.lock1 = self.lock2 = self.lock3 = self.lock4 = self.lock5 = True  
        self.check1 = self.check2 = self.check3 = self.check4 = self.check5 = True  
        self.flag = False
        self.beat_interval = 0
        self.combo_mult = 0
        self.combo = 0
        self.total_score = 0
        self.label = False
        # self.play_video()
        self.music_path = r"/home/nxorin/Downloads/novision/Merry_healthy/music/apt.mp3"
        self.osc_receive()
        # threading.Thread(target=self.play_music, args=(self.music_path,), daemon=True).start()
        # threading.Thread(target=self.osc_receive, args=(), daemon=True).start()
        
        # a=threading.Thread(target=self.osc_receive, args=(), daemon=True).start()

    def change(self,address, message):   ##接收來自pythonosc的message
        print("message")
        if not self.change_flag:
            self.change_flag = True
            self.label =True
            print("Starting")
            
            threading.Thread(target=self.play_music, args=(self.music_path,), daemon=True).start()
            time.sleep(0.5)
            threading.Thread(target=self.play_video, args=(), daemon=True).start()
        
    def osc_receive(self): 
        DISP.map("/start", self.change)
        server = ThreadingOSCUDPServer((RECEIVE_IP, PORT1), DISP)
        server.serve_forever()

    def play_music(self, music_path):     ##播放背景音樂的function
        y, sr = librosa.load(music_path)        
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)  ##利用LIBROSA取得歌曲的beat
        self.beat_times = librosa.frames_to_time(beats, sr=sr)  ##先等librosa處理完再開始播歌
        self.beat_interval = self.beat_times[10] - self.beat_times[9]  ##計算拍子間隔
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play()
        self.music_start_time = time.time()
        self.flag = True
        threading.Thread(target=self.play_beat, args=(self.beat_times,), daemon=True).start()  #####計算和顯示拍子(將剛剛計算出的beat也傳入play_beat)
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

    def score_cal(self, dif_time):   
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

        if abs(dif_time) < best:  ##根據動作與拍子的差距來計算分數
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
        print(f"總分:{self.total_score:.3f}, 此次動作加{score_add}, combo數:{self.combo}。")
        CLIENT.send_message("/score",self.total_score)
    def calculate_angle(self, a, b, c):
        a = np.array(a)  # 頭
        b = np.array(b)  # 中間點
        c = np.array(c)  # 尾

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)  # 徑轉度
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def play_beat(self, beat_times):

        self.music_start_time = time.time()  ##紀錄音樂開始時間點
        self.flag= True

        song_beat_map = {  
            "A": [8.727, 9.818, 10.909, 12, 13.091, 14.182, 15.273, 16.364, 17.455, 18.545,19.636, 20.727, 21.818, 22.909, 24, 25.091,
                26.182, 27.273, 28.364, 29.455, 30.545, 31.636, 32.727, 33.818],
            "B": [4.528, 5.66, 6.792, 7.925, 9.057, 10.189, 11.321, 12.453, 13.585, 14.717, 15.849, 16.981, 18.113, 19.245, 20.377, 
                21.509, 22.642, 23.774, 24.906, 26.038, 27.17, 28.302, 29.434, 30.566, 31.698, 32.83, 33.962, 35.094],
            "" : beat_times }    

        beat_times_list = song_beat_map[""]

        beat_count = 0

        #a = beat_times (如果要用的話，可以把註解刪去)
        for i, self.beat in enumerate(beat_times_list):   ##拍子對應的索引
            if i % 2 != 0:      #每兩拍一次(需要的話，可以把註解刪去)
                continue            
            wait_time = (self.beat) - (time.time() - self.music_start_time)  ##等待到下一個拍點的時間
                
            if wait_time > 0:  ##等到下個拍點
                time.sleep(wait_time)

            beat_count = (beat_count % 4) + 1  # 拍點1~4
            print(f"拍子{beat_count}")
            print(self.change_flag)


    def play_video(self):
        print("play video")
        cap = cv2.VideoCapture(0) #,cv2.CAP_DSHOW
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FPS, 60)
        
        framecounter = 0
        while cap.isOpened():
            success, frame = cap.read()

            frame = cv2.resize(frame, (640, 480))
            results = self.model(frame, conf=0.5, classes=0, verbose= False)
            # cv2.imshow("video",frame)
            kpt_temp = results[0].keypoints.xy 
            kpt_data = kpt_temp.cpu().numpy()  # 關鍵點data
                    
            for i in range(len(results[0].boxes)):
                body_keypoints = kpt_data[i][5:17]
                # 檢查所有關鍵點是否都偵測到condition
                if np.any(body_keypoints == 0):
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
                    if self.change_flag:
                        self.label = not self.label #########如果收到udp改變訊號，則更改邏輯，不進入下面的姿態判別式

                    if self.label & self.flag: #flag:音樂開始後的動作判斷
                        if (kpt_data[i][9][1] > kpt_data[i][5][1]) & (kpt_data[i][10][1] > kpt_data[i][6][1]) :
                            self.check1 = True
                            self.check3 = True
                            self.check4 = True
                        if (kpt_data[i][9][1] > (kpt_data[i][5][1]+kpt_data[i][11][1])/2) & (kpt_data[i][10][1] > (kpt_data[i][6][1]+kpt_data[i][12][1])/2):
                            self.check5 = True
                        
                        if( right_elbow_angle>90) & (left_elbow_angle>90):  
                            self.check2 = True

                        if(kpt_data[i][10][1] < (kpt_data[i][0][1]-((kpt_data[i][6][1]-kpt_data[i][4][1])/1.1))) & \
                            (kpt_data[i][9][1] < (kpt_data[i][0][1]-((kpt_data[i][5][1]-kpt_data[i][3][1])/1.1))) & self.lock1 & self.check1:  # 動作一(雙手舉高舉直)
                            self.check1 = False
                            self.lock1 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat
                            aa = threading.Thread(target=self.score_cal, args=(dif_time,))
                            aa.start()
                            # CLIENT.send_message("/testtt", [1]) #type
                            # CLIENT.send_message("/start", [1])
                            cool = threading.Timer(self.cool_time, self.unlock, args=('1',))   ##動作時間冷卻
                            cool.start()  


                        if(kpt_data[i][10][1] < kpt_data[i][6][1]) & (kpt_data[i][9][1] < kpt_data[i][5][1]) & \
                            (right_elbow_angle < 90) & (left_elbow_angle < 90) & (left_hand_should_angle > 140) & \
                            (np.abs(kpt_data[i][8][0]-kpt_data[i][7][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*2)) & self.lock2 \
                             & self.check2:  # 動作二(雙手低舉)
                            self.check2 = False
                            self.lock2 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat
                            bb = threading.Thread(target=self.score_cal, args=(dif_time,))
                            bb.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('2',))   ##動作時間冷卻
                            cool.start()  
                                              

                        if (right_elbow_angle > 90) & (kpt_data[i][10][1] < kpt_data[i][1][1]) & \
                            (kpt_data[i][9][1] > kpt_data[i][5][1]) & (left_body_angle < 40) & self.lock3 & self.check3:  # 動作三:右手舉高
                            self.check3 = False
                            self.lock3 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat
                            cc = threading.Thread(target=self.score_cal, args=(dif_time,))
                            cc.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('3',))   ##動作時間冷卻
                            cool.start()  

                        if (left_elbow_angle > 90) & (kpt_data[i][9][1] < kpt_data[i][2][1]) & \
                              (kpt_data[i][10][1] > kpt_data[i][6][1]) & (right_body_angle < 40) & self.lock4 & self.check4:  # 動作四:左手舉高
                            self.check4 = False
                            self.lock4 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat
                            dd = threading.Thread(target=self.score_cal, args=(dif_time,))
                            dd.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('4',))   ##動作時間冷卻
                            cool.start()  

                        if (left_elbow_angle > 130) & (right_elbow_angle > 130) & (both_hands_angle > 130) & \
                            (right_body_angle > 70) & \
                            (left_body_angle > 70) & \
                            (np.abs(kpt_data[i][10][0]-kpt_data[i][9][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*3.2))& self.lock5 & self.check5 :  # 動作五:雙手張開
                            self.check5= False
                            # self.check2 = True
                            self.lock5 = False
                            self.last_score_add_time = time.time()
                            active_time = time.time()-self.music_start_time
                            nearest_beat = min(self.beat_times, key=lambda b: abs(b - active_time))  
                            dif_time = active_time - nearest_beat
                            ee = threading.Thread(target=self.score_cal, args=(dif_time,))
                            ee.start()
                            cool = threading.Timer(self.cool_time, self.unlock, args=('5',))   ##動作時間冷卻
                            cool.start()   
                    
            framecounter += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":    
    model = YOLO(r"/home/nxorin/Downloads/novision/Merry_healthy/yolo11n-pose_ncnn_model")
    video_path = 0 #r"C:\Users\user\Desktop\Merry\音樂健康\WIN_20250424_11_01_38_Pro.mp4"
    
    label = False
    app = Interface(model, video_path, label)
