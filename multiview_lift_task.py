import sys
import numpy as np
import pygame

from robosuite.wrappers import GymWrapper
import robosuite as suite
from joystick_control import Controller
from Robosuite_Lift_Env_Multiview import MultiViewWrapper


# Environment settings
controller_type = "JOINT_VELOCITY"
control_freq = 20

# Initialize joystick controller
joystick = Controller(control_mode=controller_type)

# Create environment with all available cameras
env_name="Lift"
env = suite.make(
    env_name=env_name,
    robots="UR5e",
    controller_configs=suite.load_controller_config(default_controller=controller_type),
    has_renderer=True,
    use_object_obs=True,
    use_camera_obs=False,
    camera_names=["agentview", "birdview", "sideview", "robot0_robotview"],  # Available "camera" names
    has_offscreen_renderer=False,
    camera_heights=256,
    camera_widths=256,
    control_freq=control_freq,
)

# Add custom wrapper and gym wrapper
env = MultiViewWrapper(env, env_name)
env = GymWrapper(env)

# Enable visualization settings
for setting in env.env.get_visualization_settings():
    env.env.set_visualization_setting(setting, True)

# Main control loop
try:
    while True:
        obs = env.reset()
        done = False
        while not done:
            # Handle pygame events
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    pygame.quit()
                    sys.exit()

            # Get and apply actions
            action = joystick.get_actions()
            if action is not None:
                obs, reward, done, info = env.step(action)

            # Render all views
            env.render()
            
            # Small delay to prevent busy-waiting
            pygame.time.wait(10)

except KeyboardInterrupt:
    print("\nExiting...")
    env.close()
    pygame.quit()
    sys.exit()