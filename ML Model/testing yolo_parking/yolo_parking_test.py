import cv2
import os
from ultralytics import YOLO
import matplotlib.pyplot as plt

print("🚀 Script started successfully!")

# Load the trained YOLO model
model = YOLO("../best.pt")
print("Model loaded successfully!")

# Paths
test_images_dir = "../images"
output_dir = "./output_images"
os.makedirs(output_dir, exist_ok=True)

print(f"Checking test images directory: {test_images_dir}")
print(f"Exists? {os.path.exists(test_images_dir)} | Is a directory? {os.path.isdir(test_images_dir)}")

# Get list of images
image_files = [f for f in os.listdir(test_images_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
print(f"Found {len(image_files)} test images in {test_images_dir}")

def process_image(image_path):
    """Runs YOLO model on a single image and returns the processed image."""
    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)

    if img is None:
        print(f"Error loading image: {image_path}")
        return None

    print(f"Successfully loaded {image_path}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = model(img)  # Run YOLO on the image
    print("YOLO inference ran successfully!")

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            conf = box.conf[0].item()  # Confidence score
            class_id = int(box.cls[0].item())  # Class ID
            label = "Car" if class_id == 0 else "Empty"
            color = (255, 0, 0) if class_id == 0 else (0, 255, 0)  # Red for cars, green for empty spots

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return img

# Process each test image
for image_file in image_files:
    print(f"Processing: {image_file}")
    image_path = os.path.join(test_images_dir, image_file)

    processed_img = process_image(image_path)

    if processed_img is None:
        print(f"Skipping {image_file}, could not process.")
        continue

    # Save the output image
    output_path = os.path.join(output_dir, image_file)
    print(f"Attempting to save: {output_path}")
    
    success = cv2.imwrite(output_path, cv2.cvtColor(processed_img, cv2.COLOR_RGB2BGR))
    
    if success:
        print(f"Saved image: {output_path}")
    else:
        print(f"Failed to save: {output_path}")
