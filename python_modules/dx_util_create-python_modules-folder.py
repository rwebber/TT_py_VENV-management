import os


# iz_input 1 "trigger"
# iz_output 1 "status"

def python_init(trigger):
    """
    Initialize the script and check/create the 'python_modules' folder in the project directory if the trigger is active.
    """
    # if trigger:
    #    return python_main(trigger)
    # return "Idle"  # Output status if no trigger is received
    return "init"


def python_main(trigger):
    """
    Checks if the 'python_modules' folder exists in the project directory (one level up from this script's directory).
    Creates the folder if it does not exist.
    """
    if trigger:
        try:
            # Get the project directory by moving up one level from this script's directory
            project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

            # Define the path for the 'python_modules' folder at the project level
            python_modules_path = os.path.join(project_directory, 'python_modules')

            # Check if 'python_modules' exists; create it if it does not
            if not os.path.exists(python_modules_path):
                os.makedirs(python_modules_path)
                return "'python_modules' folder created successfully"
            else:
                return "'python_modules' folder already exists"
        except Exception as e:
            print(f"Error creating folder: {e}")
            return f"Error: {e}"
    return


def python_finalize():
    """
    Finalizes the script by performing any cleanup tasks.
    This function is called when the script is deactivated in Pythoner.
    """
    # print("Script finalizing...")


if __name__ == '__main__':
    """
    This section allows the script to be run and tested in an IDE.
    It will not execute within the Pythoner plugin in Isadora.
    """
    trigger = True  # Simulate trigger activation
    print(python_init(trigger))  # Run initialization and check/create folder
    python_finalize()  # Finalize tasks
