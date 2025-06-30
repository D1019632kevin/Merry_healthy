from pythonosc import udp_client
import time

# 設定目標的 IP 和 Port
# IP = "192.168.0.90"  # 或 localhost = "127.0.0.1"
IP = "127.0.0.1"

PORT = 7676

# 建立一個 OSC client
client = udp_client.SimpleUDPClient(IP, PORT)

# 發送訊息
client.send_message("/stop", "停止動作")
time.sleep(1)
client.send_message("/start", 123)  # 傳送整數
time.sleep(1)
client.send_message("/set_speed", [0.5, 1.2])  # 傳送一個 list

print("訊息已送出！")