# %%
from sklearn.model_selection import ParameterGrid
from ultralytics import YOLO
import json
import os
import shutil
import random
import cv2
import matplotlib.pyplot as plt

# %%
json_path = "annotations.json"
images_dir = "images"
labels_dir = "labels"
data_yaml = "data.yaml"
train_dir = "dataset/train"
val_dir = "dataset/val"
os.makedirs(train_dir + "/images", exist_ok=True)
os.makedirs(train_dir + "/labels", exist_ok=True)
os.makedirs(val_dir + "/images", exist_ok=True)
os.makedirs(val_dir + "/labels", exist_ok=True)

# %%
# Load JSON annotation file
with open(json_path, "r") as f:
    data = json.load(f)

file_names = data["train"]["file_names"]
rois_list = data["train"]["rois_list"]
occupancy_list = data["train"]["occupancy_list"]

# Split dataset (80% train, 20% val)
data_pairs = list(zip(file_names, rois_list, occupancy_list))
random.shuffle(data_pairs)
split_idx = int(0.8 * len(data_pairs))
train_data = data_pairs[:split_idx]
val_data = data_pairs[split_idx:]

# %%
# Function to process and save labels
def save_labels(file_name, rois, occupancy, split):
    label_path = f"dataset/{split}/labels/" + file_name.replace(".JPG", ".txt")
    img_path = os.path.join(images_dir, file_name)
    shutil.copy(img_path, f"dataset/{split}/images/")
    
    with open(label_path, "w") as lf:
        for obj, occupied in zip(rois, occupancy):
            x_values = [p[0] for p in obj]
            y_values = [p[1] for p in obj]
            x_center = sum(x_values) / len(x_values)
            y_center = sum(y_values) / len(y_values)
            width = max(x_values) - min(x_values)
            height = max(y_values) - min(y_values)
            class_id = 0 if occupied else 1
            lf.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

# Process all data
for file_name, rois, occupancy in train_data:
    save_labels(file_name, rois, occupancy, "train")
for file_name, rois, occupancy in val_data:
    save_labels(file_name, rois, occupancy, "val")

# %%
# Write data.yaml
with open(data_yaml, "w") as f:
    f.write("train: dataset/train\n")
    f.write("val: dataset/val\n")
    f.write("nc: 2\n")
    f.write("names: ['car', 'empty']\n")

# %%
weights = YOLO('./weights/weights11.pt')
print(weights)

# %%
# Initialize the YOLO model
model = weights

# Best parameters found: {'lr0': 0.01, 'optimizer': 'Adam', 'weight_decay': 0.001}
results = model.train(
    data=data_yaml, 
    epochs=100,  # Larger number of epochs for final training
    imgsz=640,
    batch=16,
    optimizer='Adam',
    lr0=0.01,
    weight_decay=0.001
)

# %%
# Visualize sample images
def visualize_samples(split, num=5):
    img_dir = f"dataset/{split}/images"
    label_dir = f"dataset/{split}/labels"

    sample_images = random.sample(os.listdir(img_dir), num)
    
    for img_file in sample_images:
        img_path = os.path.join(img_dir, img_file)
        label_path = os.path.join(label_dir, img_file.replace(".JPG", ".txt"))

        if not os.path.exists(img_path) or not os.path.exists(label_path):
            print(f"Skipping {img_file}, missing label or image file!")
            continue

        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Could not load image {img_path}")
            continue
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        h_img, w_img, _ = img.shape
        print(f"Processing {img_file} | Shape: {img.shape}")

        with open(label_path, "r") as lf:
            labels = lf.readlines()
            print(f"Label contents for {img_file}:\n{labels}")

            for label in labels:
                class_id, x, y, w, h = map(float, label.split())

                # Convert YOLO format (normalized) to pixel coordinates
                x1 = int((x - w / 2) * w_img)
                y1 = int((y - h / 2) * h_img)
                x2 = int((x + w / 2) * w_img)
                y2 = int((y + h / 2) * h_img)

                # Ensure box stays within image bounds
                x1 = max(0, min(w_img, x1))
                y1 = max(0, min(h_img, y1))
                x2 = max(0, min(w_img, x2))
                y2 = max(0, min(h_img, y2))

                # Ignore tiny bounding boxes
                min_box_size = 10  # Minimum pixels
                if (x2 - x1) < min_box_size or (y2 - y1) < min_box_size:
                    print(f"Skipping small box: {x1, y1, x2, y2}")
                    continue

                color = (255, 0, 0) if class_id == 0 else (0, 255, 0)
                label_name = "Car" if class_id == 0 else "Empty"

                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img, label_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        plt.figure(figsize=(10, 10))  # Enlarge plot size
        plt.imshow(img)
        plt.axis("off")
        plt.show(block=True)  # Ensure the image is displayed

# Run and debug visualization
visualize_samples("train")


