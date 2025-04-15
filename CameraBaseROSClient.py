import DynamixelArmClient
import roslibpy
import time

# Initialize Dynamixel Arm
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

def view_angle_callback(msg):
    view_angle_x = msg["view_angle"]["x"]
    view_angle_y = msg["view_angle"]["y"]
    print(view_angle_x, view_angle_y)
    arm.set_joint_angle_group(DYNAMIXEL_SERVO_ID_LIST, [view_angle_x, view_angle_y])


# Initialize ROS Client
ros_client = roslibpy.Ros(host='192.168.0.189', port=9090)

# Init subscriber
subscriber = roslibpy.Topic(ros_client, "/cmd_view_angle", "geometry_msgs/Twist")
subscriber.subscribe(view_angle_callback)

# Run ROS Client
ros_client.run()




