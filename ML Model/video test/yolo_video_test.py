import cv2
import torch
from ultralytics import YOLO

# Load the trained YOLO model
model = YOLO('../best.pt')

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
    """Main function to read from a video file, run detection every N frames, and save output."""
    video_path = "videoplayback.mp4"
    output_path = "output_video.avi"  # Output video file
    process_interval = 5  # Process every N frames

    cap = cv2.VideoCapture(video_path)  # Load video file
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # Frames per second
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Frame width
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Frame height
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for AVI format

    # Initialize video writer
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    last_processed_frame = None  # Store the last processed frame

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("End of video or failed to read frame.")
            break
        
        # Process every 'process_interval' frames
        if frame_count % process_interval == 0:
            last_processed_frame = process_frame(frame)
        
        # Use the last processed frame if not processing this one
        out.write(last_processed_frame if last_processed_frame is not None else frame)

        # Display processed frame
        cv2.imshow("Parking Spot Detection - Video Test", last_processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Process stopped: \"q\" pressed")
            break

        frame_count += 1  # Increment frame counter

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"✅ Processed video saved as {output_path}")

if __name__ == "__main__":
    main()