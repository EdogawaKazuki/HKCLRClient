import cv2
import torch
import numpy as np
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

sys.path.append('../yolov5')
from utils.augmentations import letterbox

class YoloNode:
    def __init__(self):
        self.device = '0' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")

        # Load YOLOv5 model
        # self.model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s-seg.pt', device=self.device)
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device=self.device)

    def process_frame(self, frame):
        # img = letterbox(frame, 640, stride=32, auto=True)[0]  # Resize image while keeping aspect ratio
        # img = img.transpose((2, 0, 1))  # Convert HWC to CHW
        # img = np.ascontiguousarray(img)  # Ensure the image is contiguous in memory
        #
        # img = torch.from_numpy(img).to('cuda').float()
        # # img /= 255.0  # Normalize to [0, 1]
        #
        # # Add batch dimension (1, C, H, W)
        # if img.ndimension() == 3:
        #     img = img.unsqueeze(0)  # Adds batch dimension

        return self.model(frame)

    def get_bounding_box_center(self, box):
        x1, y1, x2, y2 = box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y

    def get_class_name(self, class_id):
        return self.model.names[class_id]


if __name__ == "__main__":
    # Initialize video capture from camera (change index if needed)
    cap = cv2.VideoCapture(2)

    # Check if the camera is opened
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        exit()

    yolo_node = YoloNode()

    # Loop to process each frame
    while cap.isOpened():
        ret, frame = cap.read()
        frame = cv2.flip(frame, 0)
        frame = cv2.flip(frame, 1)
        if not ret:
            print("Error: Unable to capture image from camera.")
            break

        results = yolo_node.process_frame(frame)
        print(results)
        # results.render()
        boxes = results.xyxy[0].cpu().numpy()  # Convert to NumPy array

        # Loop through the boxes and extract center coordinates
        for box in boxes:
            x1, y1, x2, y2, confidence, class_id = box  # Extract box and additional info
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            print(f"Bounding box: {x1}, {y1}, {x2}, {y2}")
            print(f"Center: {center_x}, {center_y}")
            print(f"Confidence: {confidence}")
            print(f"Class ID: {class_id}")

            # Optionally draw the bounding box on the image
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.circle(frame, (int(center_x), int(center_y)), 5, (0, 0, 255), -1)

        # Display the frame with bounding boxes and labels
        cv2.imshow('YOLO Real-Time Detection (GPU)', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break