from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
import cv2

# 建立模型
base_options = python.BaseOptions(model_asset_path=r'C:\Users\user\Desktop\Merry\pose_landmarker_lite.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False,
    num_poses=4
)
detector = vision.PoseLandmarker.create_from_options(options)

# 開啟影片
video_path = r'C:\Users\user\Desktop\Merry\音樂健康\2.mp4'
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # OpenCV BGR → RGB，建立 MediaPipe Image
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # 使用 OpenCV frame 取得尺寸
    height, width, _ = frame.shape

    # 執行姿勢偵測
    results = detector.detect(mp_image)

    # 繪製關鍵點（只繪製 index > 10，排除臉部）
    for person_id, landmarks in enumerate(results.pose_landmarks):
        for i, landmark in enumerate(landmarks):
            if i <= 10:
                continue
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        # 顯示每個人編號
        cv2.putText(frame, f'Person {person_id+1}', (10, 30 + person_id * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 顯示畫面
    frame  = cv2.resize(frame, (640,640))
    cv2.imshow("MediaPipe Pose", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
