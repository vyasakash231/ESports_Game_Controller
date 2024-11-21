import sys
import numpy as np
import pygame

from collections import deque
import matplotlib.pyplot as plt

from robosuite.wrappers import GymWrapper
import robosuite as suite


class Controller:
    def __init__(self):
        """Initialize pygame and the game controller."""
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("No game controller detected")
            sys.exit(1)        

        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        self.gripper_close = None
        
        print(f"\nInitialized {self.controller.get_name()}")
        print(f"Number of axes: {self.controller.get_numaxes()}")
        print(f"Number of buttons: {self.controller.get_numbuttons()}")
        print("\nControl Mapping:")
        print("--------------")
        print("Left Stick: First two joints (1, 2)")
        print("Right Stick: Next two joints (3, 4)")
        print("Right Trigger (RT): Joint 5")
        print("Left Trigger (LT): Joint 6")
        print("RB Button: Hold to make RT positive (release for negative)")
        print("LB Button: Hold to make LT positive (release for negative)")
        print("X Button: Open gripper")
        print("B Button: Close gripper")

    def get_actions(self):
        """Get controller inputs and convert to robot actions."""
        actions = np.zeros(7)

        # Map joysticks (first 4 DOF)
        for i in range(4):
            value = self.controller.get_axis(i)
            actions[i] = value

        # Handle triggers with polarity control
        # Right Trigger (RT) for Joint 5
        rt_value = self.controller.get_axis(4)
        rt_polarity = 1 if self.controller.get_button(7) else -1  # RB is usually button 5
        if rt_value > -0.9:  # Only register when trigger is pressed
            actions[4] = rt_polarity * (rt_value + 1) / 2  # Scale to [0, 1] then apply polarity

        # Left Trigger (LT) for Joint 6
        lt_value = self.controller.get_axis(5)
        lt_polarity = 1 if self.controller.get_button(6) else -1  # LB is usually button 4
        if lt_value > -0.9:  # Only register when trigger is pressed
            actions[5] = lt_polarity * (lt_value + 1) / 2  # Scale to [0, 1] then apply polarity

        # Apply deadzone to joystick axes
        deadzone = 0.1
        for i in range(4):  # Only apply to joystick axes
            if abs(actions[i]) < deadzone:
                actions[i] = 0.0

        # Handle gripper
        if self.controller.get_button(3):  # X button
            self.gripper_close = False
            actions[6] = 1.0  # Open
        elif self.controller.get_button(1):  # B button
            self.gripper_close = True
            actions[6] = -1.0  # Close

        # Only return actions if there's significant input
        if np.all(actions[:6] == 0) and actions[6] == 0:
            return None

        # Print the current state (for debugging)
        print("\rActions:", end=" ")
        for i, val in enumerate(actions):
            if val != 0:  # Only print non-zero values
                print(f"Joint{i}: {val:.2f}", end=" ")
        print("", end="", flush=True)

        return actions

def main():
    # Initialize controller
    joystick = Controller()

    # Environment settings
    controller_type = "JOINT_VELOCITY" 
    control_freq = 25

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

if __name__ == "__main__":
    main()