import pygame
import HKCLRROSClient
import time
import cv2
import numpy as np
from config import JOYSTICK_CONFIG, CONTROL_CONFIG, DISPLAY_CONFIG

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

class JoystickManager:
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
            joystick.quit()
    
    def connect_joystick(self, joystick_id):
        self.joystick = pygame.joystick.Joystick(joystick_id)
        self.joystick.init()
        print(self.joystick.get_name())
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
    
    def update_event(self):
        pygame.event.pump()
    
def draw_control_output(display, control_output):
    height, width = display.shape[:2]
    
    # Clear the display
    display[:] = DISPLAY_CONFIG["colors"]["background"]
    
    # Draw control output section
    output_y = height - 200
    cv2.rectangle(display, (10, output_y), (width - 10, height - 10), DISPLAY_CONFIG["colors"]["grid"], 1)
    cv2.putText(display, "Control Output", (20, output_y + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    # Draw angular velocity bar
    ang_vel_width = int((control_output["angular_velocity"] / CONTROL_CONFIG["max_angular_velocity"]) * (width - 40) / 2)
    cv2.rectangle(display, (20, output_y + 40), (width//2 - 20, output_y + 60), 
                 DISPLAY_CONFIG["colors"]["grid"], 1)
    if ang_vel_width != 0:
        color = DISPLAY_CONFIG["colors"]["movement"] if ang_vel_width > 0 else DISPLAY_CONFIG["colors"]["reverse"]
        cv2.rectangle(display, (width//4, output_y + 40), 
                     (width//4 + ang_vel_width, output_y + 60), color, -1)
    cv2.putText(display, f"Angular Velocity: {control_output['angular_velocity']:.2f}", 
                (20, output_y + 80), cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    # Draw linear velocity bar
    lin_vel_width = int((control_output["linear_velocity"] / CONTROL_CONFIG["max_velocity"]) * (width - 40) / 2)
    cv2.rectangle(display, (20, output_y + 100), (width//2 - 20, output_y + 120), 
                 DISPLAY_CONFIG["colors"]["grid"], 1)
    if lin_vel_width != 0:
        color = DISPLAY_CONFIG["colors"]["throttle"] if lin_vel_width > 0 else DISPLAY_CONFIG["colors"]["reverse"]
        cv2.rectangle(display, (width//4, output_y + 100), 
                     (width//4 + lin_vel_width, output_y + 120), color, -1)
    cv2.putText(display, f"Linear Velocity: {control_output['linear_velocity']:.2f}", 
                (20, output_y + 140), cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    # Draw view angles
    cv2.putText(display, f"View Angle X: {control_output['view_angle_x']:.1f}°", 
                (width//2 + 20, output_y + 40), cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    cv2.putText(display, f"View Angle Y: {control_output['view_angle_y']:.1f}°", 
                (width//2 + 20, output_y + 80), cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    # Draw status indicator
    status_color = DISPLAY_CONFIG["colors"]["button_pressed"] if control_output.get("is_active", False) else DISPLAY_CONFIG["colors"]["button_released"]
    cv2.circle(display, (width - 30, 30), 10, status_color, -1)
    cv2.putText(display, "Active" if control_output.get("is_active", False) else "Inactive", 
                (width - 100, 35), cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    return display

if __name__ == "__main__":
    OFFLINE = True
    joystick_manager = JoystickManager()
    joystick_manager.init()
    joystick_manager.list_joysticks()
    joystick_manager.connect_joystick(0)
    joystick = joystick_manager.joystick
    joystick_mapping = joystick_manager.joystick_mapping
    if not OFFLINE:
        ros_client = HKCLRROSClient.HKCLRROSClient()
        ros_client.connect(host='192.168.0.189', port=9090)
        ros_client.set_velocity_topic_name("/cmd_vel")
        ros_client.start_pos_listener()

    # Initialize display
    cv2.namedWindow("Joystick Control", cv2.WINDOW_NORMAL)
    display = np.zeros((DISPLAY_CONFIG["window_height"], DISPLAY_CONFIG["window_width"], 3), dtype=np.uint8)
    
    try:
        while True:
            joystick_manager.update_event()
            control_output = joystick_manager.get_control_output()
            # print(control_output)
            # Check if start command button is pressed
            is_active = joystick.get_button(joystick_mapping["button"]["start_cmd"])
            control_output["is_active"] = is_active
            if not OFFLINE:
                if is_active:
                    ros_client.set_linear_angular_vel(control_output["linear_velocity"], control_output["angular_velocity"])
                else:
                    ros_client.set_linear_angular_vel(0, 0)
            
            # Update and show display
            display = draw_control_output(display, control_output)
            cv2.imshow("Joystick Control", display)
            
            # Break loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cv2.destroyAllWindows()
        joystick_manager.quit()



