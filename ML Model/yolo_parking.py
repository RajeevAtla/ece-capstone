import cv2
from ultralytics import YOLO

# Load the trained YOLO model
model = YOLO('best.pt')

def process_frame(frame):
    """Runs YOLO model on a single frame and returns bounding box info."""
    results = model(frame)
    boxes = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            class_id = int(box.cls[0].item())
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

def main():
    """Main function to capture live video and process every N frames."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Get camera properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    process_interval = fps * 10
    frame_count = 0
    last_boxes = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Run YOLO detection every N frames
        if frame_count % process_interval == 0 or not last_boxes:
            last_boxes = process_frame(frame)

        # Draw last detections on the current frame
        output_frame = draw_boxes(frame.copy(), last_boxes)

        cv2.imshow("Parking Spot Detection", output_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Process stopped: \"q\" pressed")
            break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()