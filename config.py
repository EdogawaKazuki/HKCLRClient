# Joystick Configuration
JOYSTICK_CONFIG = {
    "PS4 Controller": {
        "axis": {
            "move_x": 0, # left stick x
            "move_y": 1, # left stick y
            "view_x": 2, # right stick x
            "view_y": 3, # right stick y
            "throttle": 4, # left trigger
            "reverse": 5, # right trigger
        },
        "button": { 
            "primary_right": 0,
            "secondary_right": 1,
            "primary_left": 2,
            "secondary_left": 3,
            "start_cmd": 9, # right trigger
            "left_shoulder": 10,
            "up": 11,
            "down": 12,
            "left": 13,
            "right": 14,
        }
    }
}

# Control Parameters
CONTROL_CONFIG = {
    "deadzone": 0.1,  # Deadzone for all axes
    "deadzone_angular_velocity": 0.05,
    "deadzone_view_angle": 0.05,
    "deadzone_throttle": 0.05,
    "deadzone_reverse": 0.05,
    "max_angular_velocity": 10.0,  # Maximum angular velocity
    "max_velocity": 10.0,  # Maximum velocity for movement
    "max_view_angle_x": 60.0,  # Maximum view angle
    "min_view_angle_x": -10.0,  # Minimum view angle
    "max_view_angle_y": 45.0,  # Maximum view angle
    "min_view_angle_y": -45.0,  # Minimum view angle
}

# Display Configuration
DISPLAY_CONFIG = {
    "window_width": 800,
    "window_height": 600,
    "colors": {
        "background": (0, 0, 0),
        "grid": (100, 100, 100),
        "movement": (0, 255, 0),
        "view": (0, 0, 255),
        "throttle": (0, 255, 0),
        "reverse": (0, 0, 255),
        "button_pressed": (0, 255, 0),
        "button_released": (100, 100, 100),
        "text": (255, 255, 255),
    },
    "text_size": 0.5,
    "text_thickness": 1,
}

# Network Configuration (if needed for future use)
NETWORK_CONFIG = {
    "host": "localhost",
    "port": 5000,
    "timeout": 1.0,
} 