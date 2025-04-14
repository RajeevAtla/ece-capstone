import cv2
import torch
import json
from datetime import datetime
from ultralytics import YOLO

# Define persistent parking spot positions manually (x1, y1, x2, y2)
predefined_spots = {
    "spot_A1": [100, 50, 200, 150],
    "spot_A2": [220, 50, 320, 150],
    "spot_B1": [100, 160, 200, 260],
    "spot_B2": [220, 160, 320, 260],
}

model = YOLO('../best.pt')

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    if interArea == 0:
        return 0.0

    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def process_frame(frame):
    results = model(frame)
    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            class_id = int(box.cls[0].item())
            label = "Car" if class_id == 0 else "Empty"
            detections.append((x1, y1, x2, y2, label, conf))
    return detections

def match_to_spots(detections):
    matched = {}
    for spot_id, spot_box in predefined_spots.items():
        best_iou = 0
        best_label = "empty"
        for (x1, y1, x2, y2, label, conf) in detections:
            det_box = [x1, y1, x2, y2]
            iou = compute_iou(spot_box, det_box)
            if iou > best_iou and iou > 0.3:  # IoU threshold
                best_iou = iou
                best_label = "occupied" if label == "Car" else "empty"
        matched[spot_id] = best_label
    return matched

def draw_spot_boxes(frame, matched_status):
    for spot_id, (x1, y1, x2, y2) in predefined_spots.items():
        status = matched_status.get(spot_id, "empty")
        color = (0, 0, 255) if status == "occupied" else (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{spot_id} {status}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

def main():
    video_path = "IMG_6074.mov"
    output_path = "test4.avi"
    annotations_path = "annotations.json"
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
    last_status = {}
    annotation_buffer = []

    # Create or clear JSON file
    with open(annotations_path, "w") as f:
        json.dump([], f)

    flush_interval = 2 * fps  # every 2 seconds

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % process_interval == 0:
            detections = process_frame(frame)
            current_status = match_to_spots(detections)

            timestamp = datetime.now().replace(microsecond=0).isoformat()
            for spot_id, status in current_status.items():
                if spot_id not in last_status or last_status[spot_id] != status:
                    annotation_buffer.append({
                        "spot_id": spot_id,
                        "status": status,
                        "timestamp": timestamp
                    })
                    last_status[spot_id] = status

        # Flush to JSON every 2 seconds
        if frame_count % flush_interval == 0 and annotation_buffer:
            with open(annotations_path, "r+") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.extend(annotation_buffer)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            annotation_buffer = []

        # Draw static boxes and statuses
        output_frame = draw_spot_boxes(frame.copy(), last_status)
        out.write(output_frame)
        cv2.imshow("Persistent Spot Detection", output_frame)

        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break

        frame_count += 1

    # Final flush
    if annotation_buffer:
        with open(annotations_path, "r+") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.extend(annotation_buffer)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"✅ Video saved to {output_path}")
    print(f"📄 Spot-persistent annotations saved to {annotations_path}")

if __name__ == "__main__":
    main()