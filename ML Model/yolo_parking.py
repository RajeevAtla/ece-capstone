import cv2
import torch
from ultralytics import YOLO

# Load the trained YOLO model
model = YOLO('best.pt')

def process_frame(frame):
    """Runs YOLO model on a single frame and returns the processed image."""
    results = model(frame)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            conf = box.conf[0].item()  # Confidence score
            class_id = int(box.cls[0].item())  # Class ID
            label = "Car" if class_id == 0 else "Empty"
            color = (0, 0, 255) if class_id == 0 else (0, 255, 0)  # Red for cars, green for empty spots
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

def main():
    """Main function to capture video feed and run detection."""
    cap = cv2.VideoCapture(0)  # Open the default camera
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break
        
        processed_frame = process_frame(frame)
        cv2.imshow("Parking Spot Detection", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()