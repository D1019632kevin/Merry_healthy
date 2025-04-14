from pythonosc import udp_client
import time
server_ip = "192.168.0.90" 
server_port = 5005

client = udp_client.SimpleUDPClient(server_ip, server_port)

print("開始發送")
client.send_message("/test", [3]) 

# now_time = time.time()

# while True:
#     hold_time = time.time() - now_time
#     client.send_message("/test", [int(hold_time)])