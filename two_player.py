from ultralytics import YOLO
import numpy as np
import cv2
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
        self.aa_1, self.aa_2, self.bb_1, self.bb_2= False, False, False, False
        self.root.geometry("1920x1080")
        self.root.title("人體姿態偵測")
        self.temp2,self.temp3,self.temp4,self.temp5 = 0, 0, 0, 0
        self.pose_counter = 0
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
        x = int(temp1)
        CLIENT.send_message("/player1", [x])
        if temp1 == self.temp2:
            return
        sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
                      '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
                      '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
                      '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav',
                      '8':r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }

        # pygame.mixer.Sound.load(sound_dict[choose_sound])
        pygame.mixer.Sound(sound_dict[choose_sound]).play()
        self.temp2 = choose_sound

    def play_sound_p2(self, choose_sound_p2):  
        temp11 = choose_sound_p2
        y = int(temp11)
        CLIENT.send_message("/player2", [y])
        if temp11 == self.temp5:
            return
        sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
                      '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
                      '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
                      '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav',
                      '8':r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }

        # pygame.mixer.Sound.load(sound_dict[choose_sound])
        pygame.mixer.Sound(sound_dict[choose_sound_p2]).play()
        self.temp5 = choose_sound_p2

    def play_sound_1_1(self, choose_sound_1_1):  
        temp111 = choose_sound_1_1
        z = int(temp111)
        CLIENT.send_message("/player1", [z])
        if temp111 == self.temp3:
            return
        sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }

        pygame.mixer.music.load(sound_dict[choose_sound_1_1])
        pygame.mixer.music.play()
        self.temp3 = choose_sound_1_1
    def play_sound_1_2(self, choose_sound_1_2):  
        temp1111 = choose_sound_1_2
        w = int(temp1111)
        CLIENT.send_message("/player2", [w])
        if temp1111 == self.temp4:
            return
        sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\continue.mp3', '2': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A2.mp3', 
                      '3': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A3.mp3', '4': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A4.mp3',  
                      '5': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\A5.mp3',
                      '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav',
                      '8':r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }

        pygame.mixer.music.load(sound_dict[choose_sound_1_2])
        pygame.mixer.music.play()
        self.temp4 = choose_sound_1_2
        
    def stop_sound(self):
        pygame.mixer.music.stop()
        self.temp3 = None  
    # def wait(self,num):
    #     # time.sleep(0.2)
    #     self.play_sound(num)


    def play_video(self):
        self.testButton.forget()
        cap = cv2.VideoCapture(self.video_path,cv2.CAP_DSHOW) #,cv2.CAP_DSHOW
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
            frame_center  = frame.shape[1] // 2
            results = self.model(frame, conf=0.5, classes=0)
            # frame = results[0].plot()
  
            cv2.putText(frame, f"fps: {fps:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)

            kpt_temp = results[0].keypoints.xy 
            kpt_data = kpt_temp.cpu().numpy()  # 關鍵點data
            cv2.line(frame, (frame_center, 0), (frame_center, frame.shape[1]), (0, 0, 255), 5)

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
                        if(kpt_data[i][10][1] < (kpt_data[i][0][1]-((kpt_data[i][6][1]-kpt_data[i][4][1])/1.1))) & \
                            (kpt_data[i][9][1] < (kpt_data[i][0][1]-((kpt_data[i][5][1]-kpt_data[i][3][1])/1.1))):  # 動作一(雙手舉高舉直)
                            if(kpt_data[i][9][0] < frame_center) & (kpt_data[i][10][0] < frame_center):
                                # CLIENT.send_message("/player1", [1])
                                t_1 = threading.Thread(target=self.play_sound_1_1, args=('1',))
                                t_1.start()
                                # self.play_sound('1')
                                
                            elif(kpt_data[i][9][0] > frame_center) & (kpt_data[i][10][0] > frame_center):
                                # CLIENT.send_message("/player2", [1])
                                t_2 = threading.Thread(target=self.play_sound_1_2, args=('1',))
                                t_2.start()
                                
                        else:
                            if self.temp3 == '1' :
                                self.stop_sound()
                            elif self.temp4 == '1':
                                self.stop_sound()
                        

                        if(kpt_data[i][10][1] < kpt_data[i][6][1]) & (kpt_data[i][9][1] < kpt_data[i][5][1]) & \
                            (right_elbow_angle < 90) & (left_elbow_angle < 90) & (left_hand_should_angle > 140) & \
                            (np.abs(kpt_data[i][8][0]-kpt_data[i][7][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*2)):  # 動作二(雙手低舉)
                            if(kpt_data[i][9][0] < frame_center) & (kpt_data[i][10][0] < frame_center):
                                a_1 = threading.Thread(target=self.play_sound, args=('2',))
                                a_1.start()
                                # CLIENT.send_message("/player1", [2])
                            elif(kpt_data[i][9][0] > frame_center) & (kpt_data[i][10][0] > frame_center):
                                a_2 = threading.Thread(target=self.play_sound_p2, args=('2',))
                                a_2.start()
                                # CLIENT.send_message("/player2", [2])
                            # self.play_sound('2')
                            # CLIENT.send_message("/testtt", [2]) 
                                              

                        if (right_elbow_angle > 90) & (kpt_data[i][10][1] < kpt_data[i][1][1]) & \
                            (kpt_data[i][9][1] > kpt_data[i][5][1]) & (left_body_angle < 40):  # 動作三:右手舉高
                            if(kpt_data[i][9][0] < frame_center) & (kpt_data[i][10][0] < frame_center):
                                b_1 = threading.Thread(target=self.play_sound, args=('3',))
                                b_1.start()
                                # CLIENT.send_message("/player1", [3])
                            elif(kpt_data[i][9][0] > frame_center) & (kpt_data[i][10][0] > frame_center):
                                b_2 = threading.Thread(target=self.play_sound_p2, args=('3',))
                                b_2.start()
                                # CLIENT.send_message("/player2", [3])
                            # self.play_sound('3')
                            # CLIENT.send_message("/testtt", [3]) 
                            

                        if (left_elbow_angle > 90) & (kpt_data[i][9][1] < kpt_data[i][2][1]) & \
                              (kpt_data[i][10][1] > kpt_data[i][6][1]) & (right_body_angle < 40):  # 動作四:左手舉高
                            if(kpt_data[i][9][0] < frame_center) & (kpt_data[i][10][0] < frame_center):
                                c_1 = threading.Thread(target=self.play_sound, args=('4',))
                                c_1.start()
                                # CLIENT.send_message("/player1", [4])
                            elif(kpt_data[i][9][0] > frame_center) & (kpt_data[i][10][0] > frame_center):
                                c_2 = threading.Thread(target=self.play_sound_p2, args=('4',))
                                c_2.start()
                                # CLIENT.send_message("/player2", [4])
                            # self.play_sound('4')
                            # CLIENT.send_message("/testtt", [4]) 

                        if (left_elbow_angle > 110) & (right_elbow_angle > 110) & (both_hands_angle > 130) & \
                            (right_body_angle > 70) & \
                            (left_body_angle > 70) & \
                            (np.abs(kpt_data[i][10][0]-kpt_data[i][9][0]) > (np.abs(kpt_data[i][6][0]-kpt_data[i][5][0])*3.2)):  # 動作五:雙手張開
                            if(kpt_data[i][9][0] < frame_center) & (kpt_data[i][10][0] < frame_center):
                                # self.play_sound('5')
                                d_1 = threading.Thread(target=self.play_sound, args=('5',))
                                d_1.start()
                                # CLIENT.send_message("/player1", [5])
                                # CLIENT.send_message("/testtt", [5]) 
                            elif(kpt_data[i][9][0] > frame_center) & (kpt_data[i][10][0] > frame_center):
                                d_2 = threading.Thread(target=self.play_sound_p2, args=('5',))
                                d_2.start()
                                # CLIENT.send_message("/player2", [5])


                        if (left_ankle < (right_ankle - ((right_ankle-right_knee)/4))):  ##test
                            if(kpt_data[i][9][0] < frame_center) & (kpt_data[i][10][0] < frame_center):
                                self.aa_1= True
                            elif(kpt_data[i][9][0] > frame_center) & (kpt_data[i][10][0] > frame_center):
                                self.aa_2= True                         
                        if self.aa_1:
                            if (left_ankle > (right_ankle - ((right_ankle-right_knee)/5))):
                                e_1 = threading.Thread(target=self.play_sound,args=('6'))
                                e_1.start()
                                # CLIENT.send_message("/player1", [6]) 
                                self.aa_1 = False
                                # self.play_sound('6')
                        if self.aa_2:
                            if (left_ankle > (right_ankle - ((right_ankle-right_knee)/5))):
                                e_2 = threading.Thread(target=self.play_sound_p2,args=('6'))
                                e_2.start()
                                # CLIENT.send_message("/player2", [6])
                                self.aa_2 = False
                                

                        if (right_ankle < (left_ankle - ((left_ankle-left_knee)/4))):  ##test
                            if(kpt_data[i][9][0] < frame_center) & (kpt_data[i][10][0] < frame_center):
                                self.bb_1 = True
                            elif(kpt_data[i][9][0] > frame_center) & (kpt_data[i][10][0] > frame_center):
                                self.bb_2 = True
                        if self.bb_1:
                            if (right_ankle > (left_ankle - ((left_ankle-left_knee)/5))): ###################
                                f_1 = threading.Thread(target=self.play_sound,args=('7'))
                                f_1.start()
                                # CLIENT.send_message("/player1", [7]) 
                                self.bb_1 = False
                                # pydirectinput.keyDown('1')
                                # pydirectinput.keyUp('1')
                        if self.bb_2:
                            if (right_ankle > (left_ankle - ((left_ankle-left_knee)/5))): ###################
                                f_2= threading.Thread(target=self.play_sound_p2,args=('7'))
                                f_2.start()
                                # CLIENT.send_message("/player2", [7])
                                self.bb_2 = False

                        if (kpt_data[i][9][1] > kpt_data[i][13][1]) & (kpt_data[i][10][1] > kpt_data[i][14][1]):
                            self.pose_counter += 1

                        if self.pose_counter == len(results[0].boxes):
                            g_2= threading.Thread(target=self.play_sound,args=('10'))
                            g_2.start()

            self.pose_counter = 0
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
    video_path = 0 #r"C:\Users\user\Desktop\Merry\音樂健康\test.mp4"
    label = False
    app = Interface(model, video_path, root, label)
    root.mainloop()
