import os
import pandas as pd
import matplotlib.pyplot as plt

# Path to the base directory containing train, train2, ..., train50 folders
base_path = '/Users/Aman.DESKTOP-VEB4T1B/OneDrive/Documents/Rutgers/Capstone/ece-capstone/ML Model/runs/detect'

# Initialize empty list to collect DataFrames
all_data = []
current_epoch = 0

# Loop through folders from train to train50
for i in range(1, 51):
    folder_name = 'train' if i == 1 else f'train{i}'
    csv_path = os.path.join(base_path, folder_name, 'results.csv')
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['epoch'] = df['epoch'] + current_epoch  # offset epochs
        current_epoch = df['epoch'].iloc[-1] + 1  # update for next run
        all_data.append(df)
    else:
        print(f"No results.csv found in {folder_name}, skipping...")

# Concatenate all DataFrames
if not all_data:
    raise ValueError("No valid results.csv files found.")
data = pd.concat(all_data, ignore_index=True)

# Plotting (unchanged, now works on full combined data)
epochs = data['epoch']

# Training losses
plt.figure(figsize=(10, 5))
plt.plot(epochs, data['train/box_loss'], label='Train Box Loss')
plt.plot(epochs, data['train/cls_loss'], label='Train Cls Loss')
plt.plot(epochs, data['train/dfl_loss'], label='Train DFL Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Losses')
plt.legend()
plt.grid()
plt.show()

# Validation losses
plt.figure(figsize=(10, 5))
plt.plot(epochs, data['val/box_loss'], label='Val Box Loss')
plt.plot(epochs, data['val/cls_loss'], label='Val Cls Loss')
plt.plot(epochs, data['val/dfl_loss'], label='Val DFL Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Validation Losses')
plt.legend()
plt.grid()
plt.show()

# Metrics
plt.figure(figsize=(10, 5))
plt.plot(epochs, data['metrics/precision(B)'], label='Precision (B)')
plt.plot(epochs, data['metrics/recall(B)'], label='Recall (B)')
plt.plot(epochs, data['metrics/mAP50(B)'], label='mAP50 (B)')
plt.plot(epochs, data['metrics/mAP50-95(B)'], label='mAP50-95 (B)')
plt.xlabel('Epochs')
plt.ylabel('Value')
plt.title('Evaluation Metrics')
plt.legend()
plt.grid()
plt.show()

# Learning rates
plt.figure(figsize=(10, 5))
plt.plot(epochs, data['lr/pg0'], label='Learning Rate pg0')
plt.plot(epochs, data['lr/pg1'], label='Learning Rate pg1')
plt.plot(epochs, data['lr/pg2'], label='Learning Rate pg2')
plt.xlabel('Epochs')
plt.ylabel('Learning Rate')
plt.title('Learning Rates')
plt.legend()
plt.grid()
plt.show()