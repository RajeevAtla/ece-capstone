import pandas as pd
import json

# Load JSON data from the uploaded file
json_path = "vid_annotations.json"
with open(json_path, "r") as file:
    data = json.load(file)

# Convert to DataFrame
df = pd.DataFrame(data)

# Rename 'timestamp' to 'last_updated' to match the desired CSV column name
df.rename(columns={"timestamp": "last_updated"}, inplace=True)

# Save to CSV
csv_path = "parking_spots.csv"
df.to_csv(csv_path, index=False)

