import sys
import numpy as np
import pygame

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
        print("Control Mapping:")
        print("--------------")
        print("Left Stick: First two joints")
        print("Right Stick: Next two joints")
        print("Right Trigger (RT): Joint 5 (only when pressed)")
        print("Left Trigger (LT): Joint 6 (only when pressed)")
        print("X Button: Open gripper")
        print("B Button: Close gripper")

    def get_actions(self):
        """Get controller inputs and convert to robot actions."""
        actions = np.zeros(7)

        # Map joysticks (first 4 DOF)
        for i in range(4):
            value = self.controller.get_axis(i)
            actions[i] = value

        # Handle triggers (last 2 DOF) - Remap from [-1, 1] to [0, 1]
        # Right Trigger (RT) for joint 5
        rt_value = self.controller.get_axis(4)
        actions[4] = (rt_value + 1) / 2  # Remap from [-1,1] to [0,1]
        
        # Left Trigger (LT) for joint 6
        lt_value = self.controller.get_axis(5)
        actions[5] = (lt_value + 1) / 2  # Remap from [-1,1] to [0,1]

        # Apply deadzone to all axes
        deadzone = 0.1
        mask = np.abs(actions) >= deadzone
        actions = actions * mask

        # Convert -0.0 to 0.0 for cleaner printing
        actions = np.where(actions == -0.0, 0.0, actions)

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

        # Print the current state of all axes (for debugging)
        print("\rActions:", end=" ")
        for i, val in enumerate(actions):
            if val != 0:  # Only print non-zero values
                print(f"Joint{i}: {val:.2f}", end=" ")
        print("", end="", flush=True)

        return actions

if __name__ == "__main__":
    joystick = Controller()
    
    try:
        while True:
            # Handle pygame events
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            
            # Get and print actions
            actions = joystick.get_actions()
            if actions is not None:
                print(f"\rTrigger values - RT: {(joystick.controller.get_axis(4)+1)/2:.2f}, "
                      f"LT: {(joystick.controller.get_axis(5)+1)/2:.2f}", end="")
            
            # Small delay to prevent busy-waiting
            pygame.time.wait(10)

    except KeyboardInterrupt:
        print("\nExiting...")
        pygame.quit()
        sys.exit()