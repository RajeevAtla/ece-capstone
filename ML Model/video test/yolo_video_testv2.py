import cv2
import torch
import json
from datetime import datetime
from ultralytics import YOLO

from update_db import update_parking_status_from_dict  # ✅ NEW

def load_predefined_spots(json_path="predefined_spots.json"):
    with open(json_path, 'r') as f:
        return {k: tuple(v) for k, v in json.load(f).items()}

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea + 1e-5)

def process_frame_with_predefined(frame, detections, predefined_spots, iou_threshold=0.3):
    spot_status = {spot_id: "empty" for spot_id in predefined_spots}
    for det in detections:
        x1, y1, x2, y2, conf, label, _ = det
        if label != "Car":
            continue
        for spot_id, (sx1, sy1, sx2, sy2) in predefined_spots.items():
            iou = compute_iou((x1, y1, x2, y2), (sx1, sy1, sx2, sy2))
            if iou >= iou_threshold:
                spot_status[spot_id] = "occupied"
                break
    return spot_status

def draw_predefined_boxes(frame, predefined_spots, spot_status):
    for spot_id, (x1, y1, x2, y2) in predefined_spots.items():
        label = spot_status[spot_id]
        color = (0, 0, 255) if label == "occupied" else (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{spot_id} - {label}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    return frame

def main():
    video_path = "ML Model/video test/testvid2.mp4"
    output_path = "test_predefined.avi"
    predefined_spots = load_predefined_spots("predefined_spots.json")
    process_interval = 10

    model = YOLO('ML Model/best.pt')
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    frame_count = 0
    last_status = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % process_interval == 0:
            detections = []
            results = model(frame)
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = box.conf[0].item()
                    class_id = int(box.cls[0].item())
                    label = "Car" if class_id == 0 else "Empty"
                    color = (0, 0, 255) if label == "Car" else (0, 255, 0)
                    detections.append((x1, y1, x2, y2, conf, label, color))

            spot_status = process_frame_with_predefined(frame, detections, predefined_spots)

            # ✅ NEW: Update the database
            timestamp_now = datetime.now()
            update_parking_status_from_dict(spot_status, timestamp_now)

            # ✅ Draw updated status for preview
            frame = draw_predefined_boxes(frame, predefined_spots, spot_status)

        out.write(frame)
        cv2.imshow("Smart Parking - Predefined Spots", frame)
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break

        frame_count += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"✅ Video processed and saved to {output_path}")

if __name__ == "__main__":
    main()
