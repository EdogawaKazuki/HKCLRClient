import pygame
import time
import os
import cv2
import numpy as np
from config import JOYSTICK_CONFIG, CONTROL_CONFIG, DISPLAY_CONFIG

def create_control_display():
    # Create a black background
    display = np.zeros((DISPLAY_CONFIG["window_height"], DISPLAY_CONFIG["window_width"], 3), dtype=np.uint8)
    
    # Draw grid lines
    cv2.line(display, (DISPLAY_CONFIG["window_width"]//2, 0), 
             (DISPLAY_CONFIG["window_width"]//2, DISPLAY_CONFIG["window_height"]), 
             DISPLAY_CONFIG["colors"]["grid"], 1)
    cv2.line(display, (0, DISPLAY_CONFIG["window_height"]//2), 
             (DISPLAY_CONFIG["window_width"], DISPLAY_CONFIG["window_height"]//2), 
             DISPLAY_CONFIG["colors"]["grid"], 1)
    
    return display

def draw_joystick_state(display, move_axis_value, view_axis_value, throttle_value, reverse_value, 
                       primary_right_value, secondary_right_value, primary_left_value, secondary_left_value):
    height, width = display.shape[:2]
    
    # Draw movement joystick
    move_x = int(width//4 + move_axis_value[0] * width//8)
    move_y = int(height//2 + move_axis_value[1] * height//8)
    cv2.circle(display, (width//4, height//2), 50, DISPLAY_CONFIG["colors"]["grid"], 2)
    cv2.circle(display, (move_x, move_y), 20, DISPLAY_CONFIG["colors"]["movement"], -1)
    cv2.putText(display, "Movement", (width//4 - 50, height//2 - 60), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    # Add movement values
    cv2.putText(display, f"X: {move_axis_value[0]:.2f}", (width//4 - 80, height//2 + 80), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    cv2.putText(display, f"Y: {move_axis_value[1]:.2f}", (width//4 - 80, height//2 + 100), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    # Draw view joystick
    view_x = int(3*width//4 + view_axis_value[0] * width//8)
    view_y = int(height//2 + view_axis_value[1] * height//8)
    cv2.circle(display, (3*width//4, height//2), 50, DISPLAY_CONFIG["colors"]["grid"], 2)
    cv2.circle(display, (view_x, view_y), 20, DISPLAY_CONFIG["colors"]["view"], -1)
    cv2.putText(display, "View", (3*width//4 - 30, height//2 - 60), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    # Add view values
    cv2.putText(display, f"X: {view_axis_value[0]:.2f}", (3*width//4 - 80, height//2 + 80), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    cv2.putText(display, f"Y: {view_axis_value[1]:.2f}", (3*width//4 - 80, height//2 + 100), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    # Draw throttle and reverse bars
    throttle_height = int(throttle_value * height//4)
    reverse_height = int(reverse_value * height//4)
    
    cv2.rectangle(display, (width//2 - 100, height - throttle_height), 
                 (width//2 - 50, height), DISPLAY_CONFIG["colors"]["throttle"], -1)
    cv2.rectangle(display, (width//2 + 50, height - reverse_height), 
                 (width//2 + 100, height), DISPLAY_CONFIG["colors"]["reverse"], -1)
    
    # Add throttle and reverse values
    cv2.putText(display, f"Throttle: {throttle_value:.2f}", (width//2 - 100, height - 30), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    cv2.putText(display, f"Reverse: {reverse_value:.2f}", (width//2 + 50, height - 30), 
                cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    # Draw button states
    button_colors = [DISPLAY_CONFIG["colors"]["button_pressed"] if primary_right_value else DISPLAY_CONFIG["colors"]["button_released"],
                    DISPLAY_CONFIG["colors"]["button_pressed"] if secondary_right_value else DISPLAY_CONFIG["colors"]["button_released"],
                    DISPLAY_CONFIG["colors"]["button_pressed"] if primary_left_value else DISPLAY_CONFIG["colors"]["button_released"],
                    DISPLAY_CONFIG["colors"]["button_pressed"] if secondary_left_value else DISPLAY_CONFIG["colors"]["button_released"]]
    
    button_names = ["Primary R", "Secondary R", "Primary L", "Secondary L"]
    for i, (color, name) in enumerate(zip(button_colors, button_names)):
        cv2.circle(display, (width//2 - 75 + i*50, 50), 15, color, -1)
        cv2.putText(display, name, (width//2 - 90 + i*50, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, DISPLAY_CONFIG["text_size"], 
                    DISPLAY_CONFIG["colors"]["text"], DISPLAY_CONFIG["text_thickness"])
    
    return display

def check_deadzone(value):
    if value > CONTROL_CONFIG["deadzone"]:
        value = value - CONTROL_CONFIG["deadzone"]
    elif value < -CONTROL_CONFIG["deadzone"]:
        value = value + CONTROL_CONFIG["deadzone"]
    else:
        value = 0
    return value

def check_deadzone_list(value):
    for i in range(len(value)):
        value[i] = check_deadzone(value[i])
    return value

def send_command(move_axis_value, view_axis_value, throttle_value, reverse_value):
    base_angular_velocity = move_axis_value[0] * CONTROL_CONFIG["max_angular_velocity"]
    base_linear_velocity = (throttle_value - reverse_value) * CONTROL_CONFIG["max_velocity"]

    view_angle_x = view_axis_value[0] * CONTROL_CONFIG["max_view_angle"]
    view_angle_y = view_axis_value[1] * CONTROL_CONFIG["max_view_angle"]

    print(f"Base Angular Velocity: {base_angular_velocity:.2f}")
    print(f"Base Linear Velocity: {base_linear_velocity:.2f}")
    print(f"View Angle X: {view_angle_x:.2f}")
    print(f"View Angle Y: {view_angle_y:.2f}")

def main():
    # Initialize pygame
    pygame.init()
    
    # Initialize the joystick module
    pygame.joystick.init()
    
    # Check if any joysticks are connected
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("No joysticks detected!")
        return
    
    print(f"Number of joysticks detected: {joystick_count}")
    
    # Initialize the first joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
    # Get joystick information
    print(f"Joystick name: {joystick.get_name()}")
    
    # Initialize OpenCV window
    cv2.namedWindow('Joystick Control', cv2.WINDOW_NORMAL)
    
    # Get controller mapping
    controller_mapping = JOYSTICK_CONFIG[joystick.get_name()]
    
    # Initialize control values
    throttle_axis = controller_mapping["axis"]["right_trigger"]
    throttle_value = 0
    
    reverse_axis = controller_mapping["axis"]["left_trigger"]
    reverse_value = 0
    
    move_axis_x = controller_mapping["axis"]["left_x"]
    move_axis_y = controller_mapping["axis"]["left_y"]
    move_axis_value = [0, 0]
    
    view_axis_x = controller_mapping["axis"]["right_x"]
    view_axis_y = controller_mapping["axis"]["right_y"]
    view_axis_value = [0, 0]
    
    primary_right = controller_mapping["button"]["primary_right"]
    secondary_right = controller_mapping["button"]["secondary_right"]
    primary_left = controller_mapping["button"]["primary_left"]
    secondary_left = controller_mapping["button"]["secondary_left"]
    
    primary_right_value = 0
    secondary_right_value = 0
    primary_left_value = 0
    secondary_left_value = 0
    
    try:
        # Main loop to read joystick input
        while True:
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            
            move_axis_value[0] = joystick.get_axis(move_axis_x)
            move_axis_value[1] = joystick.get_axis(move_axis_y)
            move_axis_value = check_deadzone_list(move_axis_value)
            
            view_axis_value[0] = joystick.get_axis(view_axis_x)
            view_axis_value[1] = joystick.get_axis(view_axis_y)
            view_axis_value = check_deadzone_list(view_axis_value)
            
            throttle_value = joystick.get_axis(throttle_axis) + 1
            throttle_value = check_deadzone(throttle_value)
            
            reverse_value = joystick.get_axis(reverse_axis) + 1
            reverse_value = check_deadzone(reverse_value)
            
            primary_right_value = joystick.get_button(primary_right)
            secondary_right_value = joystick.get_button(secondary_right)
            primary_left_value = joystick.get_button(primary_left)
            secondary_left_value = joystick.get_button(secondary_left)
            
            # Create and update display
            display = create_control_display()
            display = draw_joystick_state(display, move_axis_value, view_axis_value, 
                                        throttle_value, reverse_value,
                                        primary_right_value, secondary_right_value,
                                        primary_left_value, secondary_left_value)
            
            # Send commands
            send_command(move_axis_value, view_axis_value, throttle_value, reverse_value)
            
            # Show the display
            cv2.imshow('Joystick Control', display)
            
            # Break loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(0.01)  # Small delay to prevent overwhelming output
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Clean up
        cv2.destroyAllWindows()
        pygame.quit()

if __name__ == "__main__":
    main()
