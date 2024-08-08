import time

import roslibpy
import numpy as np


class HKCLRROSClient:
    def __init__(self):
        self.ros = None
        self.is_connected = False
        self.init = None
        self.robot_pos = None
        self.yaw = None
        self.yaw_new = None
        self.velocity_publisher = None
        self.trans_listener = None

    def create_service(self, service_name, service_type):
        return roslibpy.Service(self.ros, service_name, service_type)

    def create_subscriber(self, topic_name, topic_type, callback):
        subscriber = roslibpy.Topic(self.ros, topic_name, topic_type)
        subscriber.subscribe(callback)
        return subscriber

    def create_publisher(self, topic_name, topic_type):
        publisher = roslibpy.Topic(self.ros, topic_name, topic_type)
        publisher.advertise()
        return publisher

    def connect(self, host, port):
        self.ros = roslibpy.Ros(host=host, port=port)
        self.ros.run()
        self.is_connected = True

    def set_velocity_topic_name(self, topic_name):
        if self.velocity_publisher is not None:
            self.velocity_publisher.unadvertise()
        self.velocity_publisher = self.create_publisher(topic_name, "geometry_msgs/Twist")
        #self.set_linear_angular_vel(0, 0)

    def update_robot_pos(self, msg):
        for transform in msg['transforms']:
            child_frame_id = transform['child_frame_id']
            rotation = transform['transform']['rotation']

            if child_frame_id == 'base_link':
                self.yaw = self.quaternion_to_euler(rotation)

    def update_robot_pos1(self, msg):
        for i in range(len(msg["transforms"])):
            if msg["transforms"][i]["child_frame_id"] == "base_link":
                self.robot_pos = msg["transforms"][i]["transform"]
        for transform in msg['transforms']:
            child_frame_id = transform['child_frame_id']
            rotation = transform['transform']['rotation']

            if child_frame_id == 'base_link':
                self.yaw = self.quaternion_to_euler(rotation)

    def quaternion_to_euler(self, quaternion):
        q = np.array([quaternion['x'], quaternion['y'], quaternion['z'], quaternion['w']])
        yaw = np.degrees(np.arctan2(2 * (q[3] * q[2] + q[0] * q[1]), 1 - 2 * (q[1] ** 2 + q[2] ** 2)))
        if yaw > 0:
            return yaw
        else:
            return 360+yaw

    def start_pos_listener1(self):
        if self.trans_listener is not None:
            self.trans_listener.unsubscribe()
        self.trans_listener = self.create_subscriber("/turtle1/pose", "turtlesim/Pose",
                                                     lambda msg: self.handle_turtle_pose(msg))

    def handle_turtle_pose(self, turtle_pose_msg):
        angular_velocity = turtle_pose_msg['theta']
        if angular_velocity > 0:
            self.yaw = angular_velocity / 3.14 * 180
        else:
            self.yaw = 360 + angular_velocity / 3.14 * 180

    def start_pos_listener(self):
        if self.trans_listener is not None:
            self.trans_listener.unsubscribe()
        self.trans_listener = self.create_subscriber("/tf", "tf2_msgs/TFMessage",
                                                     lambda msg: self.update_robot_pos(msg))

    def disconnect(self):
        if self.ros is not None:
            self.ros.terminate()
        self.is_connected = False

    def set_linear_vel(self, velocity=0):
        if self.is_connected:
            self.velocity_publisher.publish(roslibpy.Message({"linear": {"x": velocity, "y": 0, "z": 0}}))

    def set_angular_vel(self, angular=0):
        if self.is_connected:
            self.velocity_publisher.publish(roslibpy.Message({"angular": {"x": 0, "y": 0, "z": angular}}))

    def set_linear_angular_vel(self, velocity=0, angular=0):
        if self.is_connected:
            self.velocity_publisher.publish(roslibpy.Message({"linear": {"x": velocity, "y": 0, "z": 0}}))
            self.velocity_publisher.publish(roslibpy.Message({"angular": {"x": 0, "y": 0, "z": angular}}))

    def shortest_rotation_direction(self,x, y):
        clockwise = (y - x) % 360
        counterclockwise = (x - y) % 360
        shortest = -0.1 if clockwise <= counterclockwise else 0.1
        return shortest

    def supersuper(self, yaw0=0):
        if self.yaw is not None:
            if self.yaw_new is None:
                self.yaw_new = self.yaw
            if abs(self.yaw-yaw0) < 0.2:
                self.set_velocity_topic_name("/cmd_vel")
                self.velocity_publisher.publish(roslibpy.Message({"angular": {"x": 0, "y": 0, "z": 0.0001}}))
                self.disconnect()
            else:
                mov_ang = self.shortest_rotation_direction(yaw0, self.yaw_new)
                self.set_velocity_topic_name("/cmd_vel")
                self.velocity_publisher.publish(roslibpy.Message({"angular": {"x": 0, "y": 0, "z": mov_ang}}))

    def get_robot_pos(self):
        return self.robot_pos

    def disconnect(self):
        if self.trans_listener is not None:
            self.trans_listener.unsubscribe()


if __name__ == "__main__":
    # 调用函数
    # ros = JS.JsTelepresentROSClient()
    # ros.connect(host='100.81.125.72', port=9090)
    # while 1:
    # ros.create_joystick(client=ros.connect(host='100.81.125.72', port=9090))

    ros_client = HKCLRROSClient()
    host = '100.81.125.72'
    port = 9090
    ros_client.connect(host, port)
    ros_client.set_velocity_topic_name("/cmd_vel")
    ros_client.start_pos_listener()
    js_ver = 0
    js_ang = 1
    a = 150
    while 1:
        ros_client.supersuper(333)
        time.sleep(0.03)
        print(ros_client.yaw)


