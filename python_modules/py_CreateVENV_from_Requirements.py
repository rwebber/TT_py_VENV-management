"""
A script to manage the creation of Python virtual environments, along with
validating folder names, checking the environment paths, and installing
required packages from a `requirements.txt` file. Includes fallback support
for `dx_system_helpers`.

The script determines the project directory, validates user-defined inputs,
checks for prerequisites, and creates a virtual environment. Additionally,
it installs Python packages listed in `requirements.txt`.

Raises:
    ImportError: On failure to import required modules.
"""

import os
import sys
import importlib

# iz_input 1 "Venv Folder Name"
# iz_input 2 "Filepath for Venv Creation"
# iz_input 3 "Trigger"
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


def python_init(venv_folder_name, venv_creation_path, izzyTrigger):
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


def python_main(venv_folder_name, venv_creation_path, izzyTrigger):
    """
    Main function to create a virtual environment and install packages from requirements.txt.

    Args:
        venv_folder_name (str): The name of the folder for the new virtual environment.
        venv_creation_path (str): The filepath where the virtual environment will be created,
                                  or an empty/non-path string for default.
        izzyTrigger (bool): Trigger to start the script execution.

    Returns:
        str: Status message indicating the outcome of the operation if Triggered.
    """
    if not izzyTrigger:
        return "Script did not run. Trigger not activated."

    # Determine the project directory
    python_modules_path = os.path.join(os.path.dirname(__file__), '')
    project_directory = os.path.abspath(os.path.join(python_modules_path, os.pardir))

    # Check if virtualenv is installed
    if not dsh.check_virtualenv_installed():
        return "Error: 'virtualenv' is not installed. Please install it using 'pip install virtualenv'."

    # Validate the folder name
    if not dsh.is_valid_folder_name(venv_folder_name):
        return "Error: Invalid characters in the virtual environment folder name."

    # Use the project directory if venv_creation_path is not provided or is not an absolute path
    if not venv_creation_path or not dsh.is_absolute_path(venv_creation_path):
        venv_creation_path = project_directory

    # Construct the full path for the new virtual environment
    full_venv_path = os.path.join(venv_creation_path, venv_folder_name)

    # Check if the directory already contains a virtual environment
    if dsh.check_existing_venv(full_venv_path):
        return f"Error: The directory '{full_venv_path}' already contains a virtual environment."

    # Determine the location of requirements.txt
    requirements_path = os.path.join(full_venv_path, 'requirements.txt')
    if not os.path.exists(requirements_path):
        requirements_path = os.path.join(project_directory, 'requirements.txt')
        if not os.path.exists(requirements_path):
            return "Error: 'requirements.txt' not found in any expected location."

    # Create the virtual environment
    success, message = dsh.create_virtual_environment(full_venv_path)
    if not success:
        return message  # Return the error message if creation failed

    # Path to the Python executable within the virtual environment
    python_executable = os.path.join(full_venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(full_venv_path, 'bin', 'python')

    # Install packages using the newly created virtual environment
    install_message = dsh.install_packages(python_executable, requirements_path)
    if "successfully" in install_message.lower():
        return f"VENV created with the required modules successfully at {full_venv_path}"
    else:
        return install_message


def python_finalize():
    """
    Finalization logic for the script.
    """
    print("Script finalizing...")

    # Remove dx_system_helpers from sys.modules to ensure it is reloaded next time
    if dsh.__name__ in sys.modules:
        del sys.modules[dsh.__name__]


if __name__ == '__main__':
    # Test inputs
    folder_name = "venvJUNK_Izzy"
    creation_path = ""  # Empty to simulate defaulting to the project directory
    trigger = True

    # Execute the main function
    result = python_main(folder_name, creation_path, trigger)
    print(result)
