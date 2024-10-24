import socket
import struct
import numpy as np
import cv2

import HKCLRROSClient

def start_server(ros_client, use_ros = True, draw_canvas = False, log_data = False,host='0.0.0.0', port=12345):
    origin_x = 0
    origin_y = 0
    # Create a UDP socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to a specific address and port
    server_socket.bind((host, port))
    print(f"Server listening on {host}:{port}")
    if draw_canvas:
        canvas_width = 1000
        canvas_height = 1000
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

        # Draw a circle
        cv2.circle(canvas, (canvas_width // 2, canvas_height // 2), 400, (0, 255, 0), 2)

    while True:
        try:
            # Receive data from the client
            data, client_address = server_socket.recvfrom(1024)

            float_count = len(data) // 4
            float_array = struct.unpack(f'{float_count}f', data)
            if log_data:
                print(f"Received from {client_address}: {float_array}")

            if draw_canvas:
                # Clear previous robot position
                temp_canvas = canvas.copy()

                # Calculate robot position (assuming first two floats are x and y)
                canvas_x = int(float_array[0] * 400 + canvas_width / 2)
                canvas_y = int(float_array[1] * 400 + canvas_height / 2)
                # Draw robot position (larger red dot)
                cv2.circle(temp_canvas, (int((canvas_x - origin_x) // 100 + canvas_width // 2),
                                         int((canvas_y - origin_y) // 100 + canvas_height // 2)), 10, (0, 0, 255), -1)
                cv2.imshow('Data', temp_canvas)
                key = cv2.waitKey(1)
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    break
                if key == ord('c'):
                    origin_x = canvas_x
                    origin_y = canvas_y

            if use_ros:
                cmd_x = float_array[0] / 100
                cmd_y = float_array[1] / 100
                ros_client.set_linear_angular_vel(cmd_x, cmd_y)



        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    ROS_IP = "192.168.2.115"
    ROS_port = 12345
    vel_cmd_topic_Name = "/cmd_vel"
    use_ros = False
    draw_canvas = False
    log_data = True
    # init robot arm
    robot = HKCLRROSClient.HKCLRROSClient()
    if use_ros:
        robot.connect(ROS_IP, ROS_port)
        robot.set_velocity_topic_name(vel_cmd_topic_Name)
    start_server(robot, use_ros, draw_canvas, log_data)
