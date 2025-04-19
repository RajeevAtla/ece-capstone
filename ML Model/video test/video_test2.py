import cv2
import torch
from ultralytics import YOLO

# Load the trained YOLO model
model = YOLO('../best.pt')

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
            color = (0, 0, 255) if class_id == 0 else (0, 255, 0)  # Red for cars, green for empty spots
            boxes.append((x1, y1, x2, y2, conf, label, color))
    return boxes  # Return bounding box data instead of modifying the frame

def draw_boxes(frame, boxes):
    """Draws bounding boxes from stored results on a given frame."""
    for (x1, y1, x2, y2, conf, label, color) in boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

def main():
    """Main function to read a video file, run detection every N frames, and maintain original speed."""
    video_path = "IMG_6072-2.mp4"
    output_path = "test.avi"
    process_interval = 20  # Run YOLO every N frames

    cap = cv2.VideoCapture(video_path)  # Load video file
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for AVI format

    # Initialize video writer
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    last_boxes = []  # Store last detected boxes

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video or failed to read frame.")
            break
        
        # Run YOLO only every 'process_interval' frames and update stored boxes
        if frame_count % process_interval == 0 or not last_boxes:
            last_boxes = process_frame(frame)  # Store new detections
        
        # Draw stored bounding boxes on the current frame
        output_frame = draw_boxes(frame.copy(), last_boxes)

        out.write(output_frame)
        cv2.imshow("Parking Spot Detection - Video Test", output_frame)

        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):  # Maintain original framerate
            print("Process stopped: \"q\" pressed")
            break

        frame_count += 1  # Increment frame counter

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"✅ Processed video saved as {output_path}")

if __name__ == "__main__":
    main()