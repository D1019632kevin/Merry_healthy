from ultralytics import YOLO
import numpy as np
import cv2
import pydirectinput
import tkinter as tk
from PIL import Image, ImageTk
import threading
from threading import Timer
from pythonosc import udp_client
from playsound import playsound
import time

IP = "192.168.0.90" 
PORT = 7676
CLIENT = udp_client.SimpleUDPClient(IP, PORT)

class Interface:
    def __init__(self, model, video_path, root, label):
        self.model = model
        self.stop = True
        self.flag = False
        self.pressed = True
        self.video_path = video_path
        self.root = root
        self.label = label
        self.sound_dict = {}
        self.cooldown_check_1= True
        self.root.geometry("1920x1080")
        self.root.title("人體姿態偵測")
        
        self.title_frame = tk.Frame(root)
        self.title_frame.pack(expand=True, fill="both")
        self.title_label = tk.Label(self.title_frame, text='人體姿態偵測', font=('標楷體', 30))
        self.title_label.pack(ipadx=20, ipady=20, pady=(0, 40))
        
        self.video_frame = tk.Frame(root)
        self.video_frame.pack(expand=True, fill="both")
    
        self.video = tk.Label(self.video_frame)
        self.video.pack(pady=(10, 10))

        self.testButton = tk.Button(self.root, text='開始辨識', bd=6, width=15, height=2, 
                            font=('標楷體', 20), command=self.play_video)
        self.testButton.pack(anchor="center", pady=(20, 40))
        
        self.endButton = tk.Button(self.root, text='結束', bd=6, width=15, height=2, 
                            font=('標楷體', 20), command=self.root.destroy)

    def reset_flag(self):
      self.flag = False
      self.stop = True
      self.pressed = False
    
    def cooldown(self, cooldown_check_1):
        self.cooldown_check_1 = cooldown_check_1
        self.cooldown_check_1 = False
        cv2.waitKey(2000)
        self.cooldown_check_1 = True
        

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
        sound_dict = {'1': 'C:/Users/user/Desktop/Merry/Voice/1.mp3', '2': 'C:/Users/user/Desktop/Merry/Voice/2.mp3', ################
                      '3': 'C:/Users/user/Desktop/Merry/Voice/3.mp3', '4': 'C:/Users/user/Desktop/Merry/Voice/4.mp3',  
                      '5': 'C:/Users/user/Desktop/Merry/Voice/5.mp3', 
                      'a': 'C:/Users/user/Desktop/Merry/Voice/a.mp3', 'b': 'C:/Users/user/Desktop/Merry/Voice/b.mp3',  
                      'c': 'C:/Users/user/Desktop/Merry/Voice/c.mp3', 'd': 'C:/Users/user/Desktop/Merry/Voice/d.mp3' 
                }
        playsound(sound_dict[choose_sound])


    def play_video(self):
        self.testButton.forget()
        cap = cv2.VideoCapture(self.video_path) #,cv2.CAP_DSHOW
        
        self.endButton.pack(anchor="center", pady=(15, 40))
        now = time.time()
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue   
            current = time.time()
            fps = 1 / (current - now)
            now = current

            frame = cv2.resize(frame, (720, 480))
            framecenter = frame.shape[1]/2
            results = self.model(frame, conf=0.5, classes=0)
            # frame = results[0].plot()  
            cv2.putText(frame, f"fps: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            kpt_temp = results[0].keypoints.xy 
            kpt_data = kpt_temp.cpu().numpy()  # 取得關鍵點data
            # cv2.line(frame, (frame.shape[1] // 2, 0), (frame.shape[1] // 2, frame.shape[1]), (0, 0, 255), 5)

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video.imgtk = imgtk
            self.video.configure(image=imgtk)
            self.video.update()
            
            for i in range(len(results[0].boxes)):
                person_keypoints = kpt_data[i]
                body_keypoints = kpt_data[i][5:16]
                print(body_keypoints)

                # 檢查所有關鍵點是否都偵測到condition
                if np.any(person_keypoints == 0):
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
                    try_angle = self.calculate_angle(  
                        [kpt_data[i][9][0], kpt_data[i][9][1]],
                        [kpt_data[i][5][0], kpt_data[i][5][1]],
                        [kpt_data[i][6][0], kpt_data[i][6][1]]
                    )

                    self.label = True
                    if self.label:
                        if(kpt_data[i][10][1] < kpt_data[i][0][1]) & (kpt_data[i][9][1] < kpt_data[i][0][1]):  # 動作一(雙手舉高舉直)
                            if (kpt_data[i][0][0] < framecenter) & self.cooldown_check_1:
                                # t = threading.Thread(target=self.play_sound, args=('1',))
                                # t.start()
                                CLIENT.send_message("/testtt", [1])

                            else:
                                # t = threading.Thread(target=self.play_sound, args=('1',))
                                # t.start()
                                CLIENT.send_message("/testtt", [1])  
                                pydirectinput.keyDown('1')  
                                pydirectinput.keyUp('1')

                        if(kpt_data[i][10][1] < kpt_data[i][6][1]) & (kpt_data[i][9][1] < kpt_data[i][5][1]) & (right_elbow_angle < 90) & (left_elbow_angle < 90) & (left_hand_should_angle > 140):  # 動作二(雙手低舉(投降))
                            if (kpt_data[i][0][0] < framecenter):
                                # t = threading.Thread(target=self.play_sound, args=('2',))
                                # t.start()
                                CLIENT.send_message("/testtt", [2]) 
                                pydirectinput.keyDown('2')  
                                pydirectinput.keyUp('2')
                            else:
                                # t = threading.Thread(target=self.play_sound, args=('2',))
                                # t.start()
                                CLIENT.send_message("/testtt", [2]) 
                                pydirectinput.keyDown('2')  
                                pydirectinput.keyUp('2')
                        

                        if (right_elbow_angle > 90) & (kpt_data[i][10][1] < kpt_data[i][1][1]) & (kpt_data[i][9][1] > kpt_data[i][5][1]) & (left_body_angle < 40):  # 動作三:右手舉高
                            if (kpt_data[i][0][0] < framecenter):
                                # t = threading.Thread(target=self.play_sound, args=('3',))
                                # t.start()
                                CLIENT.send_message("/testtt", [3]) 
                                pydirectinput.keyDown('3') 
                                pydirectinput.keyUp('3') 
                            else:
                                # t = threading.Thread(target=self.play_sound, args=('3',))
                                # t.start()
                                CLIENT.send_message("/testtt", [3]) 
                                pydirectinput.keyDown('3')
                                pydirectinput.keyUp('3')

                        if (left_elbow_angle > 90) & (kpt_data[i][9][1] < kpt_data[i][2][1]) & (kpt_data[i][10][1] > kpt_data[i][6][1]) & (right_body_angle < 40):  # 動作四:左手舉高
                            if (kpt_data[i][0][0] < framecenter):
                                # t = threading.Thread(target=self.play_sound, args=('4',))
                                # t.start()
                                CLIENT.send_message("/testtt", [4]) 
                                pydirectinput.keyDown('4')  
                                pydirectinput.keyUp('4')
                            else:
                                # t = threading.Thread(target=self.play_sound, args=('4',))
                                # t.start()
                                CLIENT.send_message("/testtt", [4]) 
                                pydirectinput.keyDown('4')  
                                pydirectinput.keyUp('4')   
                        
                        if (left_elbow_angle > 120) & (right_elbow_angle > 120) & (both_hands_angle > 150) & (right_body_angle > 70) & (left_body_angle > 70):  # 動作五:雙手張開(記錄當下眼睛和手軸位置切四段)
                            self.flag = True
                            
                            res_t = Timer(3,self.reset_flag)
                            res_t.start()
                            temp_eye_y = kpt_data[i][1][1]
                            temp_elbow_y = kpt_data[i][7][1]

                            while self.stop:
                                last_eye_y = temp_eye_y
                                last_elbow_y = temp_elbow_y
                                segment = last_elbow_y - last_eye_y
                                self.stop = False

                        if self.flag:
                            if (kpt_data[i][0][0] < framecenter):
                                # t = threading.Thread(target=self.play_sound, args=('5',))
                                # t.start()
                                if (try_angle > 175):
                                    CLIENT.send_message("/testtt", [5]) 
                                    pydirectinput.keyDown('5') 
                                    pydirectinput.keyUp('5')
                                
                                if ((temp_elbow_y < (last_elbow_y -3)) & (temp_elbow_y>(last_elbow_y-(segment/4)))):
                                    # t = threading.Thread(target=self.play_sound, args=('a',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [6]) 
                                    pydirectinput.keyDown('a') 
                                    pydirectinput.keyUp('a') 

                                if ((temp_elbow_y<(last_elbow_y-(segment/4))) & (temp_elbow_y>(last_elbow_y-(2*segment/4)))):
                                    # t = threading.Thread(target=self.play_sound, args=('b',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [7]) 
                                    pydirectinput.keyDown('b') 
                                    pydirectinput.keyUp('b') 

                                if ((temp_elbow_y<(last_elbow_y-(2*segment/4))) & (temp_elbow_y>(last_elbow_y-(3*segment/4)))):
                                    # t = threading.Thread(target=self.play_sound, args=('c',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [8]) 
                                    pydirectinput.keyDown('c') 
                                    pydirectinput.keyUp('c') 
                                    
                                if ((temp_elbow_y < (last_eye_y))):
                                    # t = threading.Thread(target=self.play_sound, args=('d',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [9]) 
                                    pydirectinput.keyDown('d') 
                                    pydirectinput.keyUp('d') 

                            else:
                                # t = threading.Thread(target=self.play_sound, args=('5',))
                                # t.start()
                                if (try_angle > 175):
                                    CLIENT.send_message("/testtt", [5]) 
                                    pydirectinput.keyDown('5') 
                                    pydirectinput.keyUp('5') 


                                if ((temp_elbow_y<(last_elbow_y-3)) & (temp_elbow_y>(last_elbow_y-(segment/4)))):
                                    # t = threading.Thread(target=self.play_sound, args=('a',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [6]) 
                                    pydirectinput.keyDown('a') 
                                    pydirectinput.keyUp('a') 

                                if ((temp_elbow_y<(last_elbow_y-(segment/4))) & (temp_elbow_y>(last_elbow_y-(2*segment/4)))):
                                    # t = threading.Thread(target=self.play_sound, args=('b',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [7]) 
                                    pydirectinput.keyDown('b') 
                                    pydirectinput.keyUp('b') 

                                if ((temp_elbow_y<(last_elbow_y-(2*segment/4))) & (temp_elbow_y>(last_elbow_y-(3*segment/4)))):
                                    # t = threading.Thread(target=self.play_sound, args=('c',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [8]) 
                                    pydirectinput.keyDown('c') 
                                    pydirectinput.keyUp('c') 
                                    
                                if ((temp_elbow_y < (last_eye_y))):
                                    # t = threading.Thread(target=self.play_sound, args=('d',))
                                    # t.start()
                                    CLIENT.send_message("/testtt", [9]) 
                                    pydirectinput.keyDown('d') 
                                    pydirectinput.keyUp('d') 
        
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.close_app()


if __name__ == "__main__":    
    model = YOLO(r"C:\Users\user\Desktop\Merry\weight\yolo11m-pose_fp16.engine")
    root = tk.Tk()
    video_path = r"C:\Users\user\Desktop\Merry\test.mp4"
    label = False
    app = Interface(model, video_path, root, label)
    root.mainloop()