import sys
import numpy as np
import pygame

from robosuite.wrappers import GymWrapper
import robosuite as suite
from joystick_control import Controller


# Environment settings
controller_type = "JOINT_VELOCITY" 
control_freq = 25

# Environment settings
joystick = Controller(control_mode=controller_type)

# Create environment instance
env_suite = suite.make(
    env_name="Lift",
    robots="UR5e",
    controller_configs=suite.load_controller_config(default_controller=controller_type),
    has_renderer=True,
    use_object_obs=True,
    use_camera_obs=False,
    render_camera="frontview",
    has_offscreen_renderer=False,
    horizon=500,
    reward_shaping=True,
    control_freq=control_freq)

# Wrap environment
env = GymWrapper(env_suite)

print("\nControl Mapping:")
print("--------------")
print("Left Stick: X-Y movement")
print("Right Stick: Z movement and rotation")
print("X Button: Open gripper")
print("B Button: Close gripper")
print("Press Ctrl+C to exit")

try:
    while True:
        obs = env.reset()
        done = False
        
        while not done:
            # Render environment
            env.render()
            
            # Process pygame events
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    pygame.quit()
                    sys.exit()

            # Get and apply actions
            action = joystick.get_actions()
            if action is not None:
                print(f"Action: {action}")
                next_obs, reward, done, info = env.step(action)
                obs = next_obs  # Update observation
                
                # if reward != 0:
                #     print(f"Reward: {reward:.3f}")

except KeyboardInterrupt:
    print("\nExiting...")
    env.close()
    pygame.quit()
    sys.exit()