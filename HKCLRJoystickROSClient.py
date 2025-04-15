import pygame
import HKCLRROSClient
import time
from config import JOYSTICK_CONFIG, CONTROL_CONFIG

def check_deadzone(value, deadzone):
    if value > deadzone:
        value = value - deadzone
    elif value < -deadzone:
        value = value + deadzone
    else:
        value = 0
    return value

def check_deadzone_list(value, deadzone):
    for i in range(len(value)):
        value[i] = check_deadzone(value[i], deadzone)
    return value

class Joystick:
    def __init__(self):
        self.joystick = None
        self.joystick_name = None
        self.joystick_id = None
        self.joystick_mapping = None
        self.joystick_mapping_name = None
        self.control_output = {
            "move_axis_x": 0,
            "move_axis_y": 0,
            "view_axis_x": 0,
            "view_axis_y": 0,
            "throttle": 0,
            "reverse": 0
        }
    def init(self):
        pygame.init()
        pygame.joystick.init()

    def list_joysticks(self):
        joystick_count = pygame.joystick.get_count()
        if joystick_count == 0:
            print("No joysticks detected!")
            return
        print(f"Number of joysticks detected: {joystick_count}")
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            print(f"Joystick {i} name: {joystick.get_name()}")
            print(f"Joystick {i} id: {joystick.get_id()}")
    
    def connect_joystick(self, joystick_id):
        self.joystick = pygame.joystick.Joystick(joystick_id)
        self.joystick.init()
        self.joystick_name = self.joystick.get_name()
        self.joystick_id = self.joystick.get_id()
        self.joystick_mapping = JOYSTICK_CONFIG[self.joystick_name]
    
    def disconnect_joystick(self):
        self.joystick.quit()
    
    def quit(self):
        pygame.quit()

    def get_control_output(self):
        view_angle_x = self.joystick.get_axis(self.joystick_mapping["axis"]["view_x"])
        view_angle_x = check_deadzone(view_angle_x, CONTROL_CONFIG["deadzone_view_angle"])
        view_angle_x = max(min(view_angle_x, CONTROL_CONFIG["max_view_angle_x"]), CONTROL_CONFIG["min_view_angle_x"])
        view_angle_y = self.joystick.get_axis(self.joystick_mapping["axis"]["view_y"])
        view_angle_y = check_deadzone(view_angle_y, CONTROL_CONFIG["deadzone_view_angle"])
        view_angle_y = max(min(view_angle_y, CONTROL_CONFIG["max_view_angle_y"]), CONTROL_CONFIG["min_view_angle_y"])
        
        angular_velocity = self.joystick.get_axis(self.joystick_mapping["axis"]["move_x"])
        angular_velocity = check_deadzone(angular_velocity, CONTROL_CONFIG["deadzone_angular_velocity"])
        angular_velocity = angular_velocity * CONTROL_CONFIG["max_angular_velocity"]

        throttle = self.joystick.get_axis(self.joystick_mapping["axis"]["throttle"])
        throttle = check_deadzone(throttle, CONTROL_CONFIG["deadzone_throttle"])
        reverse = self.joystick.get_axis(self.joystick_mapping["axis"]["reverse"])
        reverse = check_deadzone(reverse, CONTROL_CONFIG["deadzone_reverse"])
        linear_velocity = (throttle - reverse) * CONTROL_CONFIG["max_velocity"]

        result = {
            "angular_velocity": angular_velocity,
            "view_angle_x": view_angle_x,
            "view_angle_y": view_angle_y,
            "linear_velocity": linear_velocity
        }
        return result
    
if __name__ == "__main__":
    joystick = Joystick()
    joystick.init()
    joystick.list_joysticks()
    joystick.connect_joystick(0)
    print(joystick.get_control_output())

    ros_client = HKCLRROSClient.HKCLRROSClient()
    ros_client.connect(host='192.168.0.189', port=9090)
    ros_client.set_velocity_topic_name("/cmd_vel")
    ros_client.start_pos_listener()

    while True:
        control_output = joystick.get_control_output()
        if joystick.joystick.get_button(joystick.joystick_mapping["button"]["start_cmd"]):
            ros_client.set_linear_angular_vel(control_output["linear_velocity"], control_output["angular_velocity"])
        else:
            ros_client.set_linear_angular_vel(0, 0)
        time.sleep(0.01)



