from ultralytics import YOLO
import numpy as np
import cv2
import pydirectinput
import pygame
import tkinter as tk
from PIL import Image, ImageTk
import threading
from threading import Timer
from pythonosc import udp_client
import time
import matplotlib.pyplot as plt

IP = "192.168.0.90" 
PORT = 7676
CLIENT = udp_client.SimpleUDPClient(IP, PORT)
pygame.mixer.init()
class Interface:
    def __init__(self, model, video_path, root, label):
        self.model = model
        self.video_path = video_path
        self.root = root
        self.label = label
        self.sound_dict = {}
        self.aa= False
        self.bb = False
        self.root.geometry("1920x1080")
        self.root.title("人體姿態偵測")
        self.temp2 = 0
        self.temp3 = 0
        self.fpstemp = []
        
        self.title_frame = tk.Frame(root)
        # self.title_frame.pack(expand=True, fill="both")
        self.title_label = tk.Label(self.title_frame, text='人體姿態偵測', font=('標楷體', 20))
        # self.title_label.pack(ipadx=20,  pady=(0, 10))
        
        self.video_frame = tk.Frame(root)
        self.video_frame.pack(expand=True, fill="both")
    
        self.video = tk.Label(self.video_frame)
        self.video.pack(pady=(0, 10))

        self.testButton = tk.Button(self.root, text='開始辨識', bd=6, width=15, height=2, 
                            font=('標楷體', 20), command=self.play_video)
        self.testButton.pack(anchor="center", pady=(20, 40))
        
        self.endButton = tk.Button(self.root, text='結束', bd=6, width=15, height=2, 
                            font=('標楷體', 20), command=self.root.destroy)  #command=self.fps_visiualize
    
    def calculate_angle(self, a, b, c):
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
        sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }

        # pygame.mixer.Sound.load(sound_dict[choose_sound])
        pygame.mixer.Sound(sound_dict[choose_sound]).play()
        self.temp2 = choose_sound

    def play_sound_1(self, choose_sound):  
        temp1 = choose_sound
        if temp1 == self.temp3:
            return
        sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }

        pygame.mixer.music.load(sound_dict[choose_sound])
        pygame.mixer.music.play()
        self.temp3 = choose_sound
        
    def play_sound_2(self, choose_sound):  
        temp1 = choose_sound
        if temp1 == self.temp3:
            return
        sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }
        # pygame.mixer.Sound.load()
        pygame.mixer.Sound(sound_dict[choose_sound]).play()
        self.temp3 = choose_sound

    def stop_sound(self):
        pygame.mixer.music.stop()
        self.temp3 = None  
    def wait(self,num):
        # time.sleep(0.2)
        self.play_sound_2(num)



    def play_video(self):
        self.testButton.forget()
        cap = cv2.VideoCapture(self.video_path, cv2.CAP_DSHOW) #,cv2.CAP_DSHOW
        framecounter = 0
        self.endButton.pack(anchor="center", pady=(5, 10))
        now = time.time()
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue
            current = time.time()
            if framecounter % 5 == 0 :
                fps = 1 / (current - now)
                self.fpstemp.append(fps)
            now = current

            frame = cv2.resize(frame, (1080, 720))
            results = self.model(frame, conf=0.5, classes=0)
            # frame = results[0].plot()
  
            cv2.putText(frame, f"fps: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            kpt_temp = results[0].keypoints.xy 
            kpt_data = kpt_temp.cpu().numpy()  # 關鍵點data
            # cv2.line(frame, (frame.shape[1] // 2, 0), (frame.shape[1] // 2, frame.shape[1]), (0, 0, 255), 5)

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video.imgtk = imgtk
            self.video.configure(image=imgtk)
            self.video.update()
            
            for i in range(len(results[0].boxes)):
                body_keypoints = kpt_data[i][5:17]
                left_ankle = kpt_data[i][15][1]
                left_knee = kpt_data[i][13][1]
                right_ankle = kpt_data[i][16][1]
                right_knee = kpt_data[i][14][1]

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
                    self.label = True
                    if self.label:
                        if(kpt_data[i][10][1] < (kpt_data[i][0][1]-((kpt_data[i][6][1]-kpt_data[i][4][1])/4))) & \
                            (kpt_data[i][9][1] < (kpt_data[i][0][1]-((kpt_data[i][5][1]-kpt_data[i][3][1])/4))):  # 動作一(雙手舉高舉直)
                            # t = threading.Thread(target=self.play_sound_1, args=('1',))
                            # t.start()
                            # self.play_sound('1')
                            CLIENT.send_message("/testtt", [1])
                        else:
                            if self.temp3 == '1':
                                self.stop_sound()
                        

                        if(kpt_data[i][10][1] < kpt_data[i][6][1]) & (kpt_data[i][9][1] < kpt_data[i][5][1]) & \
                            (right_elbow_angle < 90) & (left_elbow_angle < 90) & (left_hand_should_angle > 140) & \
                            (np.abs(kpt_data[i][8][0]-kpt_data[i][7][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*2)):  # 動作二(雙手低舉)
                            # a = threading.Thread(target=self.play_sound, args=('2',))
                            # a.start()
                            # self.play_sound('2')
                            CLIENT.send_message("/testtt", [2]) 
                                              

                        if (right_elbow_angle > 90) & (kpt_data[i][10][1] < kpt_data[i][1][1]) & \
                            (kpt_data[i][9][1] > kpt_data[i][5][1]) & (left_body_angle < 40):  # 動作三:右手舉高
                            # b = threading.Thread(target=self.play_sound, args=('3',))
                            # b.start()
                            # self.play_sound('3')
                            CLIENT.send_message("/testtt", [3]) 
                            

                        if (left_elbow_angle > 90) & (kpt_data[i][9][1] < kpt_data[i][2][1]) & \
                              (kpt_data[i][10][1] > kpt_data[i][6][1]) & (right_body_angle < 40):  # 動作四:左手舉高
                            # c = threading.Thread(target=self.play_sound, args=('4',))
                            # c.start()
                            # self.play_sound('4')
                            CLIENT.send_message("/testtt", [4]) 

                        if (left_elbow_angle > 110) & (right_elbow_angle > 110) & (both_hands_angle > 130) & \
                            (right_body_angle > 70) & \
                            (left_body_angle > 70) & \
                            (np.abs(kpt_data[i][10][0]-kpt_data[i][9][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*2)):  # 動作五:雙手張開
                            # self.play_sound('5')
                            # d = threading.Thread(target=self.play_sound, args=('5',))
                            # d.start()
                            CLIENT.send_message("/testtt", [5]) 

                        if (left_ankle < (right_ankle - ((right_ankle-right_knee)/4))):  ##test
                            self.aa= True
                            CLIENT.send_message("/testtt", [6]) 
                        if self.aa:
                            if (left_ankle > (right_ankle - ((right_ankle-right_knee)/5))):
                                # e = threading.Thread(target=self.wait,args=('6'))
                                # e.start()

                                self.aa = False
                                # self.play_sound('6')
                                # pydirectinput.keyDown('0')
                                # pydirectinput.keyUp('0')
                                


                        if (right_ankle < (left_ankle - ((left_ankle-left_knee)/4))):  ##test
                            self.bb = True
                            CLIENT.send_message("/testtt", [7]) 
                        if self.bb:
                            if (right_ankle > (left_ankle - ((left_ankle-left_knee)/5))): ###################
                                # f = threading.Thread(target=self.wait,args=('7'))
                                # f.start()
                                
                                self.bb = False
                                # pydirectinput.keyDown('1')
                                # pydirectinput.keyUp('1')
                            
                    
            framecounter += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def fps_visiualize(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.fpstemp[1:], marker='o', linestyle='-', color='b', label="fps")
        plt.xlabel("frames")
        plt.ylabel("fps")
        plt.title("The fps without drawing keypoints")
        plt.ylim(10,35)
        x = sum(self.fpstemp[1:])/(len(self.fpstemp)-1)
        plt.text(0, 33, f"Avg_fps: {x:.3f}", fontsize=15, color='red')
        plt.legend()
        plt.grid()
        plt.savefig("fps_NoKeypoints.png")
        plt.show()
        self.root.destroy()



if __name__ == "__main__":    
    model = YOLO(r"C:\Users\user\Desktop\Merry\音樂健康\weight\yolo11m-pose_fp16.engine")
    root = tk.Tk()
    video_path = 0 #r"C:\Users\user\Desktop\Merry\A2.mp4"
    label = False
    app = Interface(model, video_path, root, label)
    root.mainloop()