import cv2
import torch
import numpy as np
import random_color # 確保這個文件存在且內容正確
from ultralytics import YOLO
from logger import logger
from typing import List, Tuple, Dict, Any

# Assuming 'model' and 'transform' are defined elsewhere or loaded from a file
# For this example, let's assume they are loaded as in the original code.

# --- Model Loading (重點修改這裡，指定姿勢估計模型) ---
# 下載 YOLOv8 姿勢估計模型，例如 yolov8n-pose.pt
# 或者，如果你的 NCNN 模型是姿勢估計的，請確保其路徑正確
# 注意：這裡使用 PyTorch .pt 模型進行演示，因為處理姿勢估計 NCNN 模型可能更複雜，
# NCNN 模型的關鍵點輸出格式需要具體參考其轉換方式。
# 如果你的NCNN模型是姿勢估計的，請替換為你的NCNN姿勢模型路徑。
# 例如：model = YOLO("./yolo11n_pose_ncnn_model", task="pose")
model = YOLO("./yolo11n-pose_ncnn_model", task="pose") # <-- 這裡是你姿勢估計模型的路徑 (如果是.pt文件)
                                # 如果是NCNN模型，要確保是為姿勢估計轉換的NCNN模型
                                # 例如：model = YOLO("/path/to/your/yolov8n_pose_ncnn_model", task="pose")
logger.info(f"Using device: {model.device}")
# --- End Model Loading ---


# --- Predict Function (保持不變或略作調整，如果 task="pose" 已經處理) ---
def Predict(model: Any, img: np.ndarray, classes: List[int], min_conf: float, device: str) -> List[Any]:
    """
    Using Predict Model to predict objects/poses in img.
    """
    # For pose estimation, 'classes' might not be directly used for filtering in the same way
    # as object detection, as pose models typically detect 'person' and then estimate their pose.
    # We pass it just in case, but often for pose, you might remove 'classes' if it's always 'person'.
    results = model.predict(source=img, conf=min_conf, device=device, classes=classes, verbose=False)
    return results

# --- Pose Estimation and Drawing Function (主要修改這裡) ---
def Predict_and_pose_estimate(model: Any, img: np.ndarray, classes: List[int], min_conf: float,
                              rectangle_thickness: int, text_thickness: int, device: str) -> np.ndarray:
    
    results = model.predict(source=img, conf=min_conf, device=device, classes=classes, verbose=False)

    # COCO Keypoint connections (for human pose)
    # This defines the "skeleton" lines
    # (pair of keypoint indices, e.g., (0, 1) means connect keypoint 0 to keypoint 1)
    skeleton_connections = [
        (0, 1), (0, 2), (1, 3), (2, 4),      # Head, Neck, Shoulders, Elbows
        (5, 6), (5, 7), (6, 8), (7, 9),      # Shoulders, Hips, Knees, Ankles
        (10, 11), (11, 12), (12, 13), (13, 14), # (Left, Right) Hip, Knee, Ankle
        (5, 11), (6, 12) # For torso connection (left shoulder to left hip, right shoulder to right hip)
    ]
    # Keypoint colors (you can define specific colors for different keypoints)
    keypoint_colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255)] * 3 # Example colors

    for r in results:
        # Check if keypoints are present in the results (important for pose models)
        if hasattr(r, 'keypoints') and r.keypoints is not None:
            keypoints_data = r.keypoints.xy.cpu().numpy() # x, y coordinates for each person
            scores = r.boxes.conf.cpu().numpy() # Confidence score for each detected person
            boxes = r.boxes.xyxy.cpu().numpy() # Bounding box for each detected person

            for person_idx, kps in enumerate(keypoints_data):
                person_score = scores[person_idx]
                
                # Filter by confidence for the detected person
                if person_score < min_conf:
                    continue

                # Draw bounding box (optional, but good for visualizing detected person)
                x1, y1, x2, y2 = map(int, boxes[person_idx])
                
                # Get class name (usually 'person' for pose models)
                label = model.names[int(r.boxes.cls.cpu().numpy()[person_idx])] if hasattr(model, 'names') else "person"
                color = random_color.get_random_color(label) # Use a color for the person/box
                
                cv2.rectangle(img, (x1, y1), (x2, y2), color, rectangle_thickness)
                text = f"{label} {person_score:.2f}"
                (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_thickness)
                cv2.rectangle(img, (x1, y1 - h - 5), (x1 + w, y1), color, -1)
                cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), text_thickness, cv2.LINE_AA)


                # Draw keypoints and connections
                for kp_idx, (x, y) in enumerate(kps):
                    x_int, y_int = int(x), int(y)
                    # Draw keypoint circle (only if visible/confident enough, check kps.conf if available)
                    # YOLOv8 keypoints are x,y,conf by default in kps.data
                    # Here we assume kps is already filtered by keypoint confidence internally by ultralytics
                    if x_int > 0 and y_int > 0: # Avoid drawing if keypoint is (0,0) or outside image bounds
                        cv2.circle(img, (x_int, y_int), 5, keypoint_colors[kp_idx % len(keypoint_colors)], -1) # Draw filled circle

                # Draw skeleton connections
                for connection in skeleton_connections:
                    kp1_idx, kp2_idx = connection
                    if kp1_idx < len(kps) and kp2_idx < len(kps):
                        kp1_x, kp1_y = int(kps[kp1_idx][0]), int(kps[kp1_idx][1])
                        kp2_x, kp2_y = int(kps[kp2_idx][0]), int(kps[kp2_idx][1])
                        
                        # Only draw if both keypoints are "valid" (e.g., not (0,0) or out of bounds)
                        if kp1_x > 0 and kp1_y > 0 and kp2_x > 0 and kp2_y > 0:
                            cv2.line(img, (kp1_x, kp1_y), (kp2_x, kp2_y), (0, 255, 255), rectangle_thickness) # Yellow lines for skeleton

    return img

# --- Main execution loop (修改函數調用) ---
def main():
    # Model and device configuration
    # 对于NCNN模型，我们不需要使用 model.to(device)
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # 这行可以保留，用于初始化 device 变量
    current_device = str(model.device) if hasattr(model, 'device') else 'cpu'
    logger.info(f"Using device: {current_device}")


    # OpenCV Video Capture - Change for webcam or video file
    cap = cv2.VideoCapture(0) # For webcam (usually index 0)
    # cap = cv2.VideoCapture("your_video_file.mp4") # For a video file

    if not cap.isOpened():
        logger.error("Error: Could not open video stream.")
        return

    # Print model names for user (for debugging classes if needed)
    if hasattr(model, 'names'):
        logger.info("Model supports the following classes:")
        for i, name in model.names.items():
            logger.info(f"  {i}: {name}")
    else:
        logger.warning("Model does not have a 'names' attribute. Cannot list class names.")


    while True:
        ret, frame = cap.read()
        if not ret:
            logger.info("End of video stream or error reading frame.")
            break

        # Flip the frame if necessary
        # frame = cv2.flip(frame, 1)

        # Perform pose estimation
        # For pose estimation, classes=[0] usually means detecting 'person' and then their pose.
        # If your model only detects 'person' for pose, you might omit 'classes' or set it to [0].
        processed_frame = Predict_and_pose_estimate(
            model=model,
            img=frame,
            classes=[0], # Typically 'person' (class 0) for pose estimation
            min_conf=0.5, # Confidence for detecting a person
            rectangle_thickness=2, # Thickness for bounding box and skeleton lines
            text_thickness=2,
            device=current_device
        )

        # Display results
        cv2.imshow("YOLOv8 Pose Estimation", processed_frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    class SimpleLogger:
        def info(self, message):
            print(f"[INFO] {message}")
        def error(self, message):
            print(f"[ERROR] {message}")
        def warning(self, message):
            print(f"[WARN] {message}")
    logger = SimpleLogger()

    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Please install the 'ultralytics' package: pip install ultralytics")
        exit()

    # Ensure random_color.py is in the same directory and correct
    # (Content provided in previous replies)

    main()
