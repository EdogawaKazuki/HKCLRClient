import cv2
import torch
import numpy as np
import sys

sys.path.append('../yolov5')
from utils.augmentations import letterbox



# Load YOLOv5 model and specify device (GPU if available, otherwise CPU)
device = '0' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load YOLOv5 model
# model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', device=device)  # yolov5s.pt is a small model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device=device)
# Initialize video capture from camera (change index if needed)
cap = cv2.VideoCapture(2)

# Check if the camera is opened
if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

# Loop to process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture image from camera.")
        break

    # Perform inference on the frame
    frame = cv2.flip(frame, 0)
    frame = cv2.flip(frame, 1)
    img = letterbox(frame, 640, stride=32, auto=True)[0]  # Resize image while keeping aspect ratio
    img = img.transpose((2, 0, 1))  # Convert HWC to CHW
    img = np.ascontiguousarray(img)  # Ensure the image is contiguous in memory

    img = torch.from_numpy(img).to('cuda').float()
    # img /= 255.0  # Normalize to [0, 1]

    # Add batch dimension (1, C, H, W)
    if img.ndimension() == 3:
        img = img.unsqueeze(0)  # Adds batch dimension

    results = model(img)

    # print(results)

    # Render the results on the frame
    # results.render()

    # Display the frame with bounding boxes and labels
    cv2.imshow('YOLO Real-Time Detection (GPU)', results)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
