from pythonosc import udp_client, dispatcher
import time
from pythonosc.osc_server import ThreadingOSCUDPServer

# 設定目標的 IP 和 Port
# IP = "192.168.0.90"  # 或 localhost = "127.0.0.1"
IP = "127.0.0.1"
RECEIVE_IP = "0.0.0.0"
DISP = dispatcher.Dispatcher()
PORT1 = 7676
PORT2 = 7675
# 建立一個 OSC client
def score(*args):
    print({args})

client = udp_client.SimpleUDPClient(IP, PORT1)

# 發送訊息
client.send_message("/stop", "停止動作")
time.sleep(1)
client.send_message("/start", 123)  # 傳送整數
time.sleep(1)
client.send_message("/set_speed", [0.5, 1.2])  # 傳送一個 list

print("訊息已送出！")
DISP.map("/score",score)
server = ThreadingOSCUDPServer((IP, PORT2), DISP)
server.serve_forever()