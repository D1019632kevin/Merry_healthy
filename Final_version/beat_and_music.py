import time
from PyQt5 import  QtGui
from PyQt5.QtGui import  QImage, QPixmap
import librosa
import threading
import pygame


class Main_music:
    def __init__(self, parent, ui):
        super().__init__()
        self.set = parent
        self.ui = ui
  
    def convert_pixmap_to_grayscale(self, pixmap):
        #轉成灰階格式
        image = pixmap.toImage().convertToFormat(QImage.Format_Grayscale8)
        return QPixmap.fromImage(image)

    def play_music(self, music_path):     ##播放背景音樂的function
        y, sr = librosa.load(music_path)           
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        self.beat_times = librosa.frames_to_time(beats, sr=sr)  ##先等librosa處理完再開始播歌
        self.beat_interval = self.beat_times[10] - self.beat_times[9]  ##計算拍子間隔
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play()
        threading.Thread(target=self.play_beat, args=(self.beat_times,), daemon=True).start()

    def play_beat(self, beat_times):
        for i in [self.ui.label, self.ui.label_2,self.ui.label_3,self.ui.label_4]:
            i.clear()
        self.starting = True
        self.music_start_time = time.time()

        song_beat_map = {
            "A": [8.727, 9.818, 10.909, 12, 13.091, 14.182, 15.273, 16.364, 17.455, 18.545,19.636, 20.727, 21.818, 22.909, 24, 25.091,
                26.182, 27.273, 28.364, 29.455, 30.545, 31.636, 32.727, 33.818],
            "B": [4.528, 5.66, 6.792, 7.925, 9.057, 10.189, 11.321, 12.453, 13.585, 14.717, 15.849, 16.981, 18.113, 19.245, 20.377, 
                21.509, 22.642, 23.774, 24.906, 26.038, 27.17, 28.302, 29.434, 30.566, 31.698, 32.83, 33.962, 35.094],
            "" : beat_times }    

        beat_times_list = song_beat_map[self.set.choose_song]

        beat_count = 0

        for i,label in enumerate([self.ui.label, self.ui.label_2,self.ui.label_3,self.ui.label_4]):
            label.setPixmap(self.set.pose_image[i])

        for i, label in enumerate([self.ui.label_18, self.ui.label_19, self.ui.label_28, self.ui.label_33]):
            gray_image = self.convert_pixmap_to_grayscale(self.set.pose_image[i])
            label.setPixmap(gray_image)

        note =QtGui.QPixmap(r"C:\Users\user\Desktop\Merry\音樂健康\0512\rythm1.png")
        self.ui.label_12.setPixmap(note)

        self.ui.label_beat.setText("")
        for i in [self.ui.label_combo, self.ui.label_combo_2, self.ui.label_combo_3]:
            i.setText(f"Combo ✖{self.set.combo}")

        #a = beat_times
        for i, self.set.beat in enumerate(beat_times_list):
            if not self.set.restarted:
                for label in [self.ui.label_beat,self.ui.label_29, self.ui.label_30, self.ui.label_31,self.ui.label_32,self.ui.labelVideo]:
                    label.clear()
                break
            # if i % 2 != 0:
            #     continue  # 每兩拍一次
            wait_time = (self.set.beat) - (time.time() - self.music_start_time)
                
            if wait_time > 0:  ##等到拍點
                time.sleep(wait_time)

            beat_count = (beat_count % 4) + 1  # 拍點1~4

            for loop in [self.ui.label_29, self.ui.label_30, self.ui.label_31, self.ui.label_32, self.ui.label_46, self.ui.label_16, self.ui.label_20, self.ui.label_27]: 
                loop.setText("")

            beat_dict = {
                1:(self.ui.label_29, "🔴", self.ui.label_46, "🔴"),
                2:(self.ui.label_30, "🔴",self.ui.label_16, "🔴"),
                3:(self.ui.label_31, "🔴",self.ui.label_20, "🔵"),
                4:(self.ui.label_32, "🔴",self.ui.label_27, "🔵") }
            
            if beat_count in beat_dict:
                first_stage, first_icon, second_stage, second_icon = beat_dict[beat_count]
                first_stage.setText(first_icon)
                if self.ui.stackedWidget.currentIndex() == 3:
                    second_stage.setText(second_icon)
                                        
            self.ui.label_combo.setText(f"Combo ✖{self.set.combo}")
            if self.ui.stackedWidget.currentIndex() == 3:
                self.ui.label_combo_2.setText(f"Combo ✖{self.set.combo}")

            gray_index = { 4:(3, 2,self.ui.label_4, self.ui.label_3,self.ui.label_33, self.ui.label_28),
                           3:(2, 1,self.ui.label_3, self.ui.label_2,self.ui.label_28, self.ui.label_19),
                           2:(1, 0,self.ui.label_2, self.ui.label,self.ui.label_19, self.ui.label_18),
                           1:(0, 3,self.ui.label, self.ui.label_4, self.ui.label_18, self.ui.label_33) }
            
            for i, label in enumerate([self.ui.label, self.ui.label_2, self.ui.label_3, self.ui.label_4]): 
                gray_image = self.convert_pixmap_to_grayscale(self.set.pose_image[i])
                label.setPixmap(gray_image)

            if beat_count in gray_index:
                index, gray_position, first_stage_label, first_gray, second_stage_label, second_gray = gray_index[beat_count]
                first_stage_label.setPixmap(self.set.pose_image[index])
                first_gray.setPixmap(self.convert_pixmap_to_grayscale(self.set.pose_image[gray_position]))

                if self.ui.stackedWidget.currentIndex() == 3:
                    second_stage_label.setPixmap(self.set.pose_image[index])
                    second_gray.setPixmap(self.convert_pixmap_to_grayscale(self.set.pose_image[gray_position]))

            if abs(self.set.beat - self.set.pose_timing) > self.beat_interval*0.95 :  ##如果沒做動作(重製combo)
                self.set.combo = 0
                self.ui.label_combo.setText(f"Combo ✖{self.set.combo}")
                self.ui.label_combo_2.setText(f"Combo ✖{self.set.combo}")

            if self.set.combo < 3:   ####分數combo加成重置
                self.set.bluegif.stop()
                self.ui.label_fire.clear()
                self.ui.label_fire_2.clear()

    def play_sound(self, choose_sound):  
        temp1 = choose_sound
        if temp1 == self.temp2:
            self.stop_score_and_combo = True
            return
        self.stop_score_and_combo = False
        if self.set.choose_song== 'A':
            sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc1.wav', '2': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc1.wav', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc2.wav', '4': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc2.wav',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song1\perc1.wav',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }
        elif self.set.choose_song== 'B':
            sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', '2': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav', '4': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }
        else:
            sound_dict = {'1': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', '2': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav', 
                        '3': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav', '4': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc2.wav',  
                        '5': r'C:\Users\user\Desktop\Merry\音樂健康\0512\Song2\perc1.wav',
                        '6': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_左.wav', '7': r'C:\Users\user\Desktop\Merry\音樂健康\Voice\蟋蟀V3_降噪正規化_右.wav' }


        sound =pygame.mixer.Sound(sound_dict[choose_sound])
        if temp1 =="2" or temp1 =="5":
            sound.set_volume(1)
        else :
            sound.set_volume(1)    
        sound.play()
        self.temp2 = choose_sound
    

