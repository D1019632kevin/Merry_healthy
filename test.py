from pythonosc import dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

# 建立 Dispatcher 並註冊處理函數
disp = dispatcher.Dispatcher()
def reg(a, b):
    print("stop")
    print(type(b))


disp.map("/stop", reg)


# 建立 Server 並啟動（例如在本機 0.0.0.0:7676 監聽）
ip = "0.0.0.0"   # 接收任何來源
port = 7676
server = ThreadingOSCUDPServer((ip, port), disp)
print(f"Listening on {ip}:{port}")
server.serve_forever()
