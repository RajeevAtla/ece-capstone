import cv2
import torch
import json
from datetime import datetime
from ultralytics import YOLO

# Load the trained YOLO model
model = YOLO('ML Model/best.pt')

def process_frame(frame):
    """Runs YOLO model on a single frame and returns bounding box info."""
    results = model(frame)
    boxes = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            conf = box.conf[0].item()  # Confidence score
            class_id = int(box.cls[0].item())  # Class ID
            label = "Car" if class_id == 0 else "Empty"
            color = (0, 0, 255) if class_id == 0 else (0, 255, 0)
            boxes.append((x1, y1, x2, y2, conf, label, color))
    return boxes

def draw_boxes(frame, boxes):
    """Draws bounding boxes from stored results on a given frame."""
    for (x1, y1, x2, y2, conf, label, color) in boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
def load_predefined_spots(json_path="predefined_spots.json"):
    with open(json_path, 'r') as f:
        return {k: tuple(v) for k, v in json.load(f).items()}

def compute_iou(boxA, boxB):
    # boxA and boxB: (x1, y1, x2, y2)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH
    
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    
    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)
    return iou

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
    annotations_path = "vid_annotations.json"
    model = YOLO('ML Model/best.pt')
    predefined_spots = load_predefined_spots("predefined_spots.json")
    process_interval = 10

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

    frame_count = 0
    annotations = []
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
            timestamp = datetime.now().replace(microsecond=0).isoformat()

            for spot_id, status in spot_status.items():
                if spot_id not in last_status or last_status[spot_id] != status:
                    annotations.append({
                        "spot_id": spot_id,
                        "status": status,
                        "timestamp": timestamp
                    })
                    last_status[spot_id] = status

            frame = draw_predefined_boxes(frame, predefined_spots, spot_status)

        out.write(frame)
        cv2.imshow("Smart Parking - Predefined Spots", frame)
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break

        frame_count += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    with open(annotations_path, 'w') as f:
        json.dump(annotations, f, indent=4)

    print(f"✅ Processed video saved as {output_path}")
    print(f"📄 Annotations saved to {annotations_path}")

if __name__ == "__main__":
    main()