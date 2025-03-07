import json
import pandas as pd

# Load JSON file
with open("ML Model/annotations.json", "r") as file:
    data = json.load(file)

# Extract image filenames and parking spot polygons
file_names = data["train"]["file_names"]
rois_list = data["train"]["rois_list"]

# Flatten data for CSV format
rows = []
for img_index, (file_name, rois) in enumerate(zip(file_names, rois_list)):
    for spot_id, polygon in enumerate(rois):
        # Extract bounding box from polygon points
        x_min = min(p[0] for p in polygon)
        y_min = min(p[1] for p in polygon)
        x_max = max(p[0] for p in polygon)
        y_max = max(p[1] for p in polygon)
        width = x_max - x_min
        height = y_max - y_min

        # Append row for CSV
        rows.append([file_name, spot_id, x_min, y_min, width, height])

# Convert to DataFrame
df = pd.DataFrame(rows, columns=["image_id", "spot_id", "x_min", "y_min", "width", "height"])

# Save as CSV
csv_filename = "parking_spots.csv"
df.to_csv(csv_filename, index=False)

print(f"CSV file saved as {csv_filename}")
