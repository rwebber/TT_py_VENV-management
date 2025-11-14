import os
import platform


# iz_input 1 "trigger"
# iz_output 1 "status"

def python_init(trigger):
    """
    Initialize the script and open the project root if trigger is active.
    """
    # if trigger:
    #    return python_main(trigger)
    # return "Idle"  # Output status if no trigger is received
    return "init"


def python_main(trigger):
    """
    Uses the path of the current script to locate and open the project root in the system's file explorer.
    """
    if trigger:
        try:
            # Determine the project root directory by going up one level from __file__
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

            if platform.system() == "Windows":
                os.startfile(project_root)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{project_root}"')
            else:
                return "Unsupported OS"

            return "Project root opened successfully"
        except Exception as e:
            print(f"Error opening path: {e}")
            return f"Error: {e}"
    return


def python_finalize():
    """
    Finalizes the script by cleaning up any tasks. Called when deactivated in Pythoner.
    """
    # print("Script finalizing...")


if __name__ == '__main__':
    """
    This section allows the script to run in an IDE for testing.
    This part does not execute in the Pythoner plugin.
    """
    trigger = True  # Simulate trigger activation
    print(python_init(trigger))  # Initialize and test path opening
    python_finalize()  # Finalize tasks
