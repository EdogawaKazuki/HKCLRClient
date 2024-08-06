import roslibpy


class HKCLRROSClient:
    def __init__(self):
        self.ros = None
        self.is_connected = False

        self.robot_pos = None

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
        self.set_linear_angular_vel(0, 0)

    def update_robot_pos(self, msg):
        for i in range(len(msg["transforms"])):
            if msg["transforms"][i]["child_frame_id"] == "base_link":
                self.robot_pos = msg["transforms"][i]["transform"]

    def start_pos_listener(self):
        if self.trans_listener is not None:
            self.trans_listener.unsubscribe()
        self.trans_listener = self.create_subscriber("/tf", "tf2_msgs/TFMessage", lambda msg: self.update_robot_pos(msg))

    def disconnect(self):
        if self.ros is not None:
            self.ros.terminate()
        self.is_connected = False
        
    def set_linear_vel(self,velocity=0):
        if self.is_connected:
            self.velocity_publisher.publish(roslibpy.Message({"linear": {"x": velocity, "y": 0, "z": 0}}))

    def set_angular_vel(self,angular=0):
        if self.is_connected:
            self.velocity_publisher.publish(roslibpy.Message({"angular": {"x": 0, "y": 0, "z": angular}}))
    
    def set_linear_angular_vel(self, velocity=0, angular=0):
        if self.is_connected:
            self.velocity_publisher.publish(roslibpy.Message({"linear": {"x": velocity, "y": 0, "z": 0}}))
            self.velocity_publisher.publish(roslibpy.Message({"angular": {"x": 0, "y": 0, "z": angular}}))

    def get_robot_pos(self):
        return self.robot_pos


if __name__ == "__main__":
    # 调用函数
    #ros = JS.JsTelepresentROSClient()
    #ros.connect(host='100.81.125.72', port=9090)
    #while 1:
    # ros.create_joystick(client=ros.connect(host='100.81.125.72', port=9090))

    ros_client = HKCLRROSClient()
    host = '192.168.2.136'
    port = 9090
    ros_client.connect(host, port)
    ros_client.set_velocity_topic_name("/turtle1/cmd_vel")
    ros_client.start_pos_listener()
    js_ver = 10
    js_ang = 1
    while 1:
        ros_client.set_linear_angular_vel(js_ver, js_ang)
        print(ros_client.robot_pos)
