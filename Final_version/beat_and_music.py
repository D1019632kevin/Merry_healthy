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
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)  ##利用LIBROSA取得歌曲的beat
        self.beat_times = librosa.frames_to_time(beats, sr=sr)  ##先等librosa處理完再開始播歌
        self.set.beat_interval = self.beat_times[10] - self.beat_times[9]  ##計算拍子間隔
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play()
        threading.Thread(target=self.play_beat, args=(self.beat_times,), daemon=True).start()  #####計算和顯示拍子(將剛剛計算出的beat也傳入play_beat)

    def play_beat(self, beat_times):
        for i in [self.ui.label, self.ui.label_2,self.ui.label_3,self.ui.label_4]:
            i.clear()
        self.set.starting = True
        self.set.music_start_time = time.time()  ##紀錄音樂開始時間點

        song_beat_map = {  
        ##"A"代表A歌曲的拍子,"B"代表B歌曲的拍子，""對應到第三關的Yellow那首歌(前面兩首A和B會將librosa的beat蓋掉)，若要使用librosa的beat，可以改掉，而""對應到第三關的Yellow那首歌(使用librosa)
            "A": [8.727, 9.818, 10.909, 12, 13.091, 14.182, 15.273, 16.364, 17.455, 18.545,19.636, 20.727, 21.818, 22.909, 24, 25.091,
                26.182, 27.273, 28.364, 29.455, 30.545, 31.636, 32.727, 33.818],
            "B": [4.528, 5.66, 6.792, 7.925, 9.057, 10.189, 11.321, 12.453, 13.585, 14.717, 15.849, 16.981, 18.113, 19.245, 20.377, 
                21.509, 22.642, 23.774, 24.906, 26.038, 27.17, 28.302, 29.434, 30.566, 31.698, 32.83, 33.962, 35.094],
            "" : beat_times }    

        beat_times_list = song_beat_map[self.set.choose_song]

        beat_count = 0

        for i,label in enumerate([self.ui.label, self.ui.label_2,self.ui.label_3,self.ui.label_4]):  #初始化設定動作照片(第一關)
            label.setPixmap(self.set.pose_image[i])

        for i, label in enumerate([self.ui.label_18, self.ui.label_19, self.ui.label_28, self.ui.label_33]):  #初始化設定動作照片(第二關)
            gray_image = self.convert_pixmap_to_grayscale(self.set.pose_image[i])
            label.setPixmap(gray_image)

        note =QtGui.QPixmap(r"C:\Users\user\Desktop\Merry\音樂健康\0512\rythm1.png")
        self.ui.label_12.setPixmap(note)

        self.ui.label_beat.setText("")
        for i in [self.ui.label_combo, self.ui.label_combo_2, self.ui.label_combo_3]:  ##更新combo
            i.setText(f"Combo ✖{self.set.combo}")

        #a = beat_times (如果要用的話，可以把註解刪去)
        for i, self.set.beat in enumerate(beat_times_list):   ##拍子對應的索引
            if not self.set.restarted:  ##restarted會在start_all 跟 restart的函式更改邏輯(若是按下restart會清空遊戲畫面的label)
                for label in [self.ui.label_beat,self.ui.label_29, self.ui.label_30, self.ui.label_31,self.ui.label_32,self.ui.labelVideo]:
                    label.clear()
                break
            # if i % 2 != 0:      #每兩拍一次(需要的話，可以把註解刪去)
            #     continue            
            wait_time = (self.set.beat) - (time.time() - self.set.music_start_time)  ##等待到下一個拍點的時間
                
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
                first_stage, first_icon, second_stage, second_icon = beat_dict[beat_count]  #beat_dict對應的圖標(有第一關根第二關)
                first_stage.setText(first_icon)
                if self.ui.stackedWidget.currentIndex() == 3:
                    second_stage.setText(second_icon)
                                        
            self.ui.label_combo.setText(f"Combo ✖{self.set.combo}")  ##顯示COMBO
            if self.ui.stackedWidget.currentIndex() == 3:
                self.ui.label_combo_2.setText(f"Combo ✖{self.set.combo}")

            gray_index = { 4:(3, 2,self.ui.label_4, self.ui.label_3,self.ui.label_33, self.ui.label_28),
                           3:(2, 1,self.ui.label_3, self.ui.label_2,self.ui.label_28, self.ui.label_19),
                           2:(1, 0,self.ui.label_2, self.ui.label,self.ui.label_19, self.ui.label_18),
                           1:(0, 3,self.ui.label, self.ui.label_4, self.ui.label_18, self.ui.label_33) }
            
            for i, label in enumerate([self.ui.label, self.ui.label_2, self.ui.label_3, self.ui.label_4]):   ##將遊戲一開始時，所有圖片轉灰階
                gray_image = self.convert_pixmap_to_grayscale(self.set.pose_image[i])
                label.setPixmap(gray_image)

            if beat_count in gray_index:  ##將當前拍子對應圖片顯示彩色，其餘為灰階
                index, gray_position, first_stage_label, first_gray, second_stage_label, second_gray = gray_index[beat_count]
                first_stage_label.setPixmap(self.set.pose_image[index])
                first_gray.setPixmap(self.convert_pixmap_to_grayscale(self.set.pose_image[gray_position]))

                if self.ui.stackedWidget.currentIndex() == 3:
                    second_stage_label.setPixmap(self.set.pose_image[index])  ##將當前拍子對應圖片顯示彩色，其餘為灰階(第二關)
                    second_gray.setPixmap(self.convert_pixmap_to_grayscale(self.set.pose_image[gray_position]))

            if abs(self.set.beat - self.set.pose_timing) > self.set.beat_interval*0.95 :  ##如果拍點時間內沒做動作(重製combo)
                self.set.combo = 0
                self.ui.label_combo.setText(f"Combo ✖{self.set.combo}")
                self.ui.label_combo_2.setText(f"Combo ✖{self.set.combo}")

            if self.set.combo < 3:   ####分數combo加成重置
                self.set.bluegif.stop()
                self.ui.label_fire.clear()
                self.ui.label_fire_2.clear()

    def play_sound(self, choose_sound):  ##音效播放的函式
        temp1 = choose_sound  ##temp1拿來記錄此次做的動作(避免重複動作觸發音效)
        if temp1 == self.set.temp2:   # 若是不做別的動作，temp1會跟temp2保持相同，音效就不會播放
            self.set.stop_score_and_combo = True  ##若是等於True，將會停止在score.py裡面的score_cal的分數計算
            return  ##直接返還
        self.set.stop_score_and_combo = False ##分數正常計算
        if self.set.choose_song== 'A':  ##對應音效
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
        #sound.set_volume(1)    ##可以調整音量大小
        sound.play()
        self.set.temp2 = choose_sound  ##播放完音效一次後，記錄下來(若是不做別的動作，temp1會跟temp2保持相同，音效就不會播放)    

