import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('/Users/parshvamehta/ece-capstone/ML Model/runs/detect/train39/results.csv') 

# Extracting data columns
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
plt.ylabel('Metrics')
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
