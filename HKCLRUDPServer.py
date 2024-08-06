import threading

import numpy as np

import HKCLRROSClient
import time
import struct
import socket


def bytes_to_float(byte_array, byte_order='<'):
    # Assuming the byte array represents a 32-bit floating-point number (single precision)
    float_size = 4

    # Ensure the byte array length matches the float size
    if len(byte_array) != float_size:
        raise ValueError(f"Invalid byte array length. Expected {float_size} bytes.")

    # Convert byte array to float
    format_str = f"{byte_order}f"
    return struct.unpack(format_str, byte_array)[0]


def float_to_bytes(float_num, byte_order='<'):
    # Convert float to bytes
    # print(float_num)
    byte_array = struct.pack(f"{byte_order}f", float_num)
    return byte_array


def bytes_to_int(byte_array, byte_order='little'):
    return int.from_bytes(byte_array, byte_order)


def int_to_bytes(integer, byte_order='little', signed=True):
    # Convert integer to bytes
    byte_size = 2  # Calculate the number of bytes needed
    byte_array = integer.to_bytes(byte_size, byte_order, signed=signed)
    return byte_array


def sender():
    while True:
        if not is_connected or client_addr is None or shut_down:
            print("STOP Sending")
            break
        # print("Connected: " + str(is_connected))
        robot_pos = robot.get_robot_pos()
        send_data = []
        send_data += float_to_bytes(robot_pos["translation"]["x"])
        send_data += float_to_bytes(robot_pos["translation"]["y"])
        send_data += float_to_bytes(robot_pos["translation"]["z"])
        send_data += float_to_bytes(robot_pos["rotation"]["x"])
        send_data += float_to_bytes(robot_pos["rotation"]["y"])
        send_data += float_to_bytes(robot_pos["rotation"]["z"])
        # print(servo_angle_list)
        # print(send_data)
        # print(len(send_data))
        udp_socket.sendto(bytes(send_data), client_addr)
        time.sleep(0.01)


def receiver():
    global udp_socket
    global is_connected
    global client_addr
    send_thread = None
    while True:
        if shut_down:
            break
        try:
            data, addr = udp_socket.recvfrom(1024)  # Adjust buffer size as needed
            cmd_type = data[0]
            if cmd_type == 0:
                print("Connect Message: ")
                cmd_data = data[1]
                if cmd_data == 1:
                    print("Connect")
                    is_connected = True
                    client_addr = addr
                    robot.set_linear_angular_vel(0, 0)
                    send_thread = threading.Thread(target=sender)
                    send_thread.start()
                else:
                    print("Disconnect")
                    is_connected = False
                    if send_thread is not None:
                        send_thread.join()
                    robot.set_linear_angular_vel(0, 0)
            elif cmd_type == 1:
                print("Set Vel Command")
                # print(data)
                vel_cmd = [0, 0]
                for i in range(2):
                    vel_cmd[i] = bytes_to_float(data[1 + i * 4: 1 + (i + 1) * 4], '<')
                if abs(vel_cmd[0]) < 0.01:
                    vel_cmd[0] = 0
                if abs(vel_cmd[1]) < 0.01:
                    vel_cmd[1] = 0
                robot.set_linear_angular_vel(vel_cmd[0], vel_cmd[1])
                print(f"Linear Vel: {vel_cmd[0]}, Angular Vel: {vel_cmd[1]}")
        except Exception as e:
            print(e)
            raise e


shut_down = False

ROS_IP = "192.168.2.136"
ROS_port = 9090
vel_cmd_topic_Name = "/cmd_vel"

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 1234

# init robot arm
robot = HKCLRROSClient.HKCLRROSClient()
robot.connect(ROS_IP, ROS_port)
robot.set_velocity_topic_name(vel_cmd_topic_Name)
robot.start_pos_listener()


# init socket
udp_socket = None
try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((SERVER_HOST, SERVER_PORT))
    print(f"UDP receiver started on {SERVER_HOST}:{SERVER_PORT}")
except Exception as e:
    print(f"UDP receiver start failed. Error: {e}")
    exit(-1)
is_connected = False
client_addr = None

receiver_thread = threading.Thread(target=receiver)
receiver_thread.start()
# while True:
#     try:
#         tmp = arm.get_joint_angle_group(DYNAMIXEL_SERVO_ID_LIST)
#         if tmp == -1:
#             continue
#         for i in range(len(servo_angle_list)):
#             tmp_servo_angle_list[i], tmp_servo_pwm_list[i] = tmp[i]
#         servo_angle_list[0] = tmp_servo_angle_list[0] - 180
#         servo_angle_list[1] = 270 - tmp_servo_angle_list[1]
#         servo_angle_list[2] = tmp_servo_angle_list[2] - 180
#     except KeyboardInterrupt:
#         shut_down = True
#         break
#     time.sleep(1)
# print()

receiver_thread.join()

time.sleep(1)
robot.disconnect()
