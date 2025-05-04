import cv2
import time
import tkinter as tk
from PIL import Image, ImageTk

WIDTH = 640
HEIGHT = 360
FPS = 50

class Interface:
    def __init__(self, video_path, root):
        self.cap = None
        self.video_path = video_path
        self.root = root
        self.prev_time = time.time()
        self.fps = 0
        self.framecounter = 0
        self.paused = False  # 是否暫停
        self.fpstemp = []

        self.root.geometry("800x600")
        self.root.title("即時鏡頭顯示")

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        self.pause_button = tk.Button(self.root, text="暫停/播放", command=self.toggle_pause)
        self.pause_button.pack(pady=10)

        self.cap = cv2.VideoCapture(self.video_path, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_frame()

    def toggle_pause(self):
        self.paused = not self.paused

    def update_frame(self):
        if not self.paused:
            success, frame = self.cap.read()
            if not success:
                return

            if self.framecounter == 5:
                current = time.time()
                self.fps = 5 / (current - self.prev_time)
                self.prev_time = current
                self.framecounter = 0

            self.framecounter += 1

            cv2.putText(frame, f"FPS: {self.fps:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(1, self.update_frame)

    def on_close(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    video_path = 0  # 改為 0 即為鏡頭
    app = Interface(video_path, root)
    root.mainloop()
