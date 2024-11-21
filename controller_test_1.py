import pygame
import sys
import time
import numpy as np

def init_controller():
    """Initialize pygame and the game controller."""
    pygame.init()
    pygame.joystick.init()
    
    # Check if any joystick/game controller is connected
    if pygame.joystick.get_count() == 0:
        print("No game controller detected")
        sys.exit(1)
    
    # Initialize the first controller
    joystick_obj = pygame.joystick.Joystick(0)  # Create a new Joystick object, Joystick(id) -> joystick_obj
    joystick_obj.init()  # initialize the joystick_obj
    
    print(f"\nInitialized {joystick_obj.get_name()}")
    print(f"Number of axes on a Joystick: {joystick_obj.get_numaxes()}")
    print(f"Number of buttons on a Joystick: {joystick_obj.get_numbuttons()}")
    print(f"Number of hats controls on a Joystick: {joystick_obj.get_numhats()}")

    return joystick_obj

def test_controller(joystick):
    """Main loop to test controller inputs."""
    try:
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                # Button pressed
                elif event.type == pygame.JOYBUTTONDOWN:
                    print(f"\nButton {event.button} pressed")
                
                # Button released
                elif event.type == pygame.JOYBUTTONUP:
                    print(f"Button {event.button} released")
                
                # Axis motion
                elif event.type == pygame.JOYAXISMOTION:
                    # Only print if there's significant movement (dealing with noise)
                    if abs(event.value) > 0.1:
                        print(f"Axis {event.axis} value: {event.value:.2f}")
                
                # Hat motion (D-pad)
                elif event.type == pygame.JOYHATMOTION:
                    print(f"Hat {event.hat} value: {event.value}")
            
            # Optional: add a small sleep to prevent the loop from running too fast
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        pygame.quit()

def make_action(joystick):
    """Monitor joystick actions and print when changes occur."""
    prev_action = np.zeros(6)
    
    try:
        while True:
            # Handle pygame events to prevent the program from becoming unresponsive
            pygame.event.pump()
            
            # Create a new array for current actions
            current_action = np.zeros(6)
            
            # Get joystick positions
            current_action[0] = joystick.get_axis(0)  # Left stick (left[-] <-> right[+])
            current_action[1] = joystick.get_axis(1)  # Left stick (up[-] <-> down[+])
            current_action[2] = joystick.get_axis(2)  # Right stick (left[-] <-> right[+])
            current_action[3] = joystick.get_axis(3)  # Right stick (up[-] <-> down[+])
            current_action[4] = joystick.get_axis(4)  # Right trigger (default is [-], trigger makes it [+])
            current_action[5] = joystick.get_axis(5)  # Left trigger (default is [-], trigger makes it [+])

            # Add a small threshold to prevent noise
            threshold = 0.01
            significant_change = np.any(np.abs(current_action - prev_action) > threshold)

            if significant_change:
                print("\nJoystick positions:")
                for i, value in enumerate(current_action):
                    print(f"Axis {i}: {value:.3f}")
                
                # Create a deep copy of the current action
                prev_action = np.copy(current_action)
            
            # Add a small delay to prevent the loop from running too fast
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting...")
        pygame.quit()

def main():
    print("Game Controller Test Utility")
    print("----------------------------")
    print("Press buttons, move axes, or use the d-pad to see their values")
    print("Press Ctrl+C to exit\n")
    
    joystick = init_controller()
    # test_controller(joystick)
    make_action(joystick)

if __name__ == "__main__":
    main()