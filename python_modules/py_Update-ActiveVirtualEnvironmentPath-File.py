"""
This module provides functionalities for interacting with virtual environments, including
checking for 'virtualenv' installation, validating folder names for environments, creating
and maintaining virtual environments, and finalizing script execution.

It includes fallback implementations for `dx_system_helpers` functions and
operations for updating the active virtual environment path.

"""

import os
import sys
import importlib


# iz_input 1 "Venv Creation Status"
# iz_output 1 "Status Message"


dsh = None  # module-level reference
def import_injected(module_name: str, *, reload: bool = False, strict: bool = False):
    try:
        mod = sys.modules.get(module_name)
        if mod is None:
            mod = importlib.import_module(module_name)
        elif reload:
            mod = importlib.reload(mod)
        return mod
    except Exception as e:
        print(f"Import failed for '{module_name}': {type(e).__name__}: {e}")
        print("Hint: ensure your injector actor ran and remains active, or the module is on sys.path.")
        if strict:
            raise RuntimeError(f"Required module not available: {module_name}") from e
        return None

def import_many(names, strict=True):
    # usage - code example for python_init():
    #
    # mods = import_many(["dx_system_helpers", "packaging"], strict=True)
    # if mods is None:
    #     return "INIT error"
    # dsh = mods["dx_system_helpers"]
    # pkg = mods["packaging"]
    # return "init"

    mods = {}
    try:
        for n in names:
            mods[n] = import_injected(n, strict=strict)
        return mods
    except RuntimeError as e:
        print(e)
        return None


def python_init(input_1):
    global dsh
    mName = "dx_system_helpers"
    try:
        dsh = import_injected(mName, strict=True)
        return "init"
    except RuntimeError:
        print("Unable to load injected module: " + mName)
        # or: print(f"Unable to load injected module: {mName}")
        dsh = None
        return "INIT error"


def python_main(venv_creation_status):
    """
    Updates the ActiveVirtualEnvironmentPath.txt file with the path of the newly created virtual environment.

    Args:
    venv_creation_status (str): Status message from the virtual environment creation script.

    Returns:
    str: Status message indicating the outcome of the operation.
    """

    # Check if the virtual environment was created successfully and parse the path
    if "successfully" in venv_creation_status.lower():
        try:
            venv_path = venv_creation_status.split("at ")[1]  # Extract the path
        except IndexError:
            return "Error: Unable to parse the virtual environment path."
    else:
        return "Virtual environment creation failed. No update made."

    # Define the file path for ActiveVirtualEnvironmentPath.txt based on the operating system
    if os.name == 'nt':  # Windows
        active_env_file_path = r'C:\Program Files\Common Files\TroikaTronix\Python\ActiveVirtualEnvironmentPath.txt'
    else:  # macOS and other Unix-like systems
        active_env_file_path = '/Library/Application Support/TroikaTronix/Python/ActiveVirtualEnvironmentPath.txt'

    try:
        # Check if the ActiveVirtualEnvironmentPath.txt file exists, create it if not
        os.makedirs(os.path.dirname(active_env_file_path), exist_ok=True)
        with open(active_env_file_path, 'w') as file:
            file.write(venv_path)

        return f"Updated ActiveVirtualEnvironmentPath.txt with {venv_path}"
    except IOError as e:
        return f"IOError: Failed to update ActiveVirtualEnvironmentPath.txt: {str(e)}"


def python_finalize():
    """
    Finalizes the script by performing any cleanup tasks.
    This function is called when the script is deactivated in Pythoner.
    """
    print("Script finalizing...")



if __name__ == '__main__':
    # Example input for testing
    example_status = "Virtual environment created successfully at C:\\Users\\dusxy\\OneDrive\\Desktop\\TT izzy ML project\\new_venv2"
    print(python_main(example_status))
