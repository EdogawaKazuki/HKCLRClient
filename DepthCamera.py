import json

import pyrealsense2 as rs
import numpy as np
import cv2
from YoloNode import YoloNode
import DynamixelArmClient
import time
import UDPServer
import struct


def custom_encoder(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert numpy arrays to lists
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def float_to_bytes(float_num, byte_order='<'):
    # Convert float to bytes
    # print(float_num)
    byte_array = struct.pack(f"{byte_order}f", float_num)
    return byte_array
mouse_x = 0
mouse_y = 0
# mouse callback function
def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    mouse_x = x
    mouse_y = y
    # if event == cv2.EVENT_MOUSEMOVE:
    #     # Print the current mouse position in the window
    #     point_3d = get_point_3d(x, y)
    #     # print(f"Mouse position: ({x}, {y}, {depth_image[y, x]}, {point_3d})")

def get_point_3d(x, y):
    x = int(640 - x - 1)
    y = int(480 - y - 1)
    # print(x, y)
    point_3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x, y], depth_image[y, x])
    return point_3d

def find_nearest_object_center(boxes, x, y):
    min_distance = 1000000
    nearest_center = [0 ,0]
    # class_id = "None"
    nearest_box = None
    nearest_index = -1
    index = -1
    for box in boxes:
        index += 1
        x1, y1, x2, y2, confidence, class_id = box  # Extract box and additional info
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        # point_3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [center_x, center_y], depth_image[int(center_y), int(center_x)])
        # distance = np.sqrt(point_3d[0] * point_3d[0] + point_3d[1] * point_3d[1] + point_3d[2] * point_3d[2])
        distance = np.sqrt((center_x - x) * (center_x - x) + (center_y - y) * (center_y - y))
        if distance < min_distance:
            min_distance = distance
            nearest_center = (center_x, center_y)
            nearest_box = box
            nearest_index = index

    # print(f"Nearest object center: {nearest_center}, {class_id}")
    return [nearest_box, nearest_center, nearest_index]


# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
# Set the mouse callback function for this window
cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback("RealSense", mouse_callback)

# Initialize Dynamixel Arm Client

DYNAMIXEL_ADDR = "COM16"
DYNAMIXEL_PROTOCOL = 2.0
DYNAMIXEL_BAUD_RATE = 57600
DYNAMIXEL_SERVO_ID_LIST = [15, 14]
print("Connecting to Dynamixel Arm")
arm = DynamixelArmClient.DynamixelArmClient()
arm.connect(DYNAMIXEL_ADDR, DYNAMIXEL_PROTOCOL, DYNAMIXEL_BAUD_RATE)
# arm.lock_joint_group(DYNAMIXEL_SERVO_ID_LIST)
# arm.set_joint_angle_group(DYNAMIXEL_SERVO_ID_LIST, [180, 180])
arm.release_joint_group(DYNAMIXEL_SERVO_ID_LIST)
print("Connected to Dynamixel Arm")

# Initialize YOLO node
print("Initializing YOLO node")
yolo_node = YoloNode()
detect_freq = 10
print("YOLO node initialized")

# Initialize UDP server
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1235
server = UDPServer.UDPServer(SERVER_HOST, SERVER_PORT)
server.start_server_multithread()
send_freq = 20


start_time_detect = time.time()
start_time_send = time.time()
boxes = []
print("Start processing frames")
try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
        # depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        # if depth_colormap_dim != color_colormap_dim:
        #     resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
        #     images = np.hstack((resized_color_image, depth_colormap))
        # else:
        #     images = np.hstack((color_image, depth_colormap))
        images = color_image
        images = cv2.flip(images, 1)
        images = cv2.flip(images, 0)
        if time.time() - start_time_detect > 1 / detect_freq:
            start_time_detect = time.time()
            # get the result from yolo
            result = yolo_node.process_frame(images)
            boxes = result.xyxy[0].cpu().numpy()
        objects = []
        for box in boxes:
            x1, y1, x2, y2, confidence, class_id = box
            cv2.rectangle(images, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(images, f"{yolo_node.get_class_name(class_id)}", (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255 , 0), 2)
            objects.append({"name": yolo_node.get_class_name(class_id), "confidence": confidence, "position": get_point_3d(int((x1 + x2) / 2), int((y1 + y2) / 2))})

        # Loop through the boxes and extract center coordinates
        nearest_object = find_nearest_object_center(boxes, mouse_x, mouse_y)
        box = nearest_object[0]
        if box is not None:
            x1, y1, x2, y2, confidence, class_id = box  # Extract box and additional info
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            cv2.rectangle(images, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.circle(images, (int(center_x), int(center_y)), 5, (0, 0, 255), -1)

        # print(nearest_object)
        pan_tile_angle = [x[0] for x in arm.get_joint_angle_group(DYNAMIXEL_SERVO_ID_LIST)]
        if server.is_connected:
            # send_data = []
            # for i in range(2):
                # send_data += float_to_bytes(pan_tile_angle[i])
            if (time.time() - start_time_send) > 1 / send_freq:
                send_data = {}
                send_data["pan"] = pan_tile_angle[0]
                send_data["tilt"] = pan_tile_angle[1]
                send_data["objects"] = objects
                send_data["nearest_object_index"] = nearest_object[-1]
                send_data_str = json.dumps(send_data, default=custom_encoder)
                print(send_data_str)
                send_data_bytes = bytes(send_data_str.encode('utf-8'))
                start_time_send = time.time()
                server.send_data(send_data_bytes)
        # print(arm.get_joint_angle_group(DYNAMIXEL_SERVO_ID_LIST))

        # Show images
        cv2.imshow('RealSense', images)
        cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
