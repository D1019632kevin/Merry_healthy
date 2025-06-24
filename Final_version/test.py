import cv2

# 開啟攝影機（0 為預設攝影機）
cap = cv2.VideoCapture(0)

# 檢查攝影機是否成功開啟
if not cap.isOpened():
   print("無法開啟攝影機")
   exit()

while True:
   # 讀取攝影機影格
   ret, frame = cap.read()
   
   if not ret:
       print("無法讀取影格")
       break

   # 顯示影格
   cv2.imshow('Camera', frame)

   # 按下 q 鍵離開
   if cv2.waitKey(1) & 0xFF == ord('q'):
       break

# 釋放攝影機資源
cap.release()
cv2.destroyAllWindows()
