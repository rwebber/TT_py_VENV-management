"""
This module provides functionality to retrieve and output detailed information related to the system's
environment, active user, and Python runtime configuration. It analyzes the environment to determine
specific Pythoner-related configurations and prints environment-related details formatted for debugging
or logging purposes.

Functions:
    - python_main: Core function to gather and output information regarding the Python environment.
    - python_finalize: Placeholder function for cleanup operations before deactivation.
"""

import os
import getpass
import sys

# iz_input 1 "trigger"
# iz_output 1 "Python exe path"
# iz_output 2 "Python modules path"
# iz_output 3 "Project directory"
# iz_output 4 "Pythoner config"

"""
This module retrieves and prints information about the system environment,
active user, and Python-related details such as version and executable path.
It also analyzes and outputs the current Pythoner environment configuration.

Outputs:
    1. Path to the Python executable
    2. Path to the 'python_modules' directory
    3. Path to the Isadora project directory
    4. Pythoner environment configuration string
"""

def python_main(trigger):
    # Helper function: determine Pythoner configuration
    # def detect_pythoner_config(exe_path, project_dir):
    #     # Constants for built-in paths
    #     MAC_BUILTIN_ROOT = "/Library/Application Support/TroikaTronix"
    #     WIN_BUILTIN_ROOT = r"C:\Program Files\Common Files\TroikaTronix"
    #     CONFIG_FILE_NAME = "ActiveVirtualEnvironmentPath.txt"
    #
    #     exe_path = os.path.normpath(exe_path).lower()
    #     project_dir = os.path.normpath(project_dir).lower()
    #
    #     # Option 3: Local VENV inside project folder
    #     if "venv" in exe_path and exe_path.startswith(project_dir):
    #         return "Option 3 - Local VENV"
    #
    #     # Option 1: Built-in Pythoner
    #     if MAC_BUILTIN_ROOT.lower() in exe_path or WIN_BUILTIN_ROOT.lower() in exe_path:
    #         return "Option 1 - Built-In Pythoner"
    #
    #     # Option 2: Isadora Custom VENV
    #     try:
    #         if os.name == 'nt':
    #             config_path = os.path.join(WIN_BUILTIN_ROOT, "Python", CONFIG_FILE_NAME)
    #         else:
    #             config_path = os.path.join(MAC_BUILTIN_ROOT, "Python", CONFIG_FILE_NAME)
    #
    #         if os.path.isfile(config_path):
    #             with open(config_path, 'r') as f:
    #                 venv_path = os.path.normpath(f.read().strip()).lower()
    #                 if exe_path.startswith(venv_path):
    #                     return "Option 2 - Isadora Custom VENV"
    #     except Exception as e:
    #         print("Error reading config file:", e)
    #
    #     return "Unknown Configuration"
    def detect_pythoner_config(exe_path, project_dir):
        MAC_BUILTIN_ROOT = "/Library/Application Support/TroikaTronix"
        WIN_BUILTIN_ROOT = r"C:\Program Files\Common Files\TroikaTronix"
        CONFIG_FILE_NAME = "ActiveVirtualEnvironmentPath.txt"

        # Normalize for robust comparisons (case-insensitive on Windows)
        norm = lambda p: os.path.normcase(os.path.normpath(p))
        exe_path_n = norm(exe_path)
        project_dir_n = norm(project_dir)

        # Project-local venv MUST be <project>/virtual_env
        project_local_venv = norm(os.path.join(project_dir, "virtual_env"))

        # --- Option 2: Isadora Custom VENV (from config file) ---
        try:
            config_root = WIN_BUILTIN_ROOT if os.name == 'nt' else MAC_BUILTIN_ROOT
            config_path = os.path.join(config_root, "Python", CONFIG_FILE_NAME)
            if os.path.isfile(config_path):
                with open(config_path, "r") as f:
                    venv_path = norm(f.read().strip())
                    if exe_path_n.startswith(venv_path):
                        return "Option 2 - Isadora Custom VENV"
        except Exception as e:
            print("Error reading config file:", e)

        # --- Option 3: Local VENV inside project folder at ./virtual_env ---
        # Extra sanity: ensure it looks like a venv (pyvenv.cfg exists)
        if exe_path_n.startswith(project_local_venv) and os.path.isfile(os.path.join(project_local_venv, "pyvenv.cfg")):
            return "Option 3 - Local VENV"

        # --- Option 1: Built-in Pythoner ---
        if (norm(WIN_BUILTIN_ROOT) in exe_path_n) or (norm(MAC_BUILTIN_ROOT) in exe_path_n):
            return "Option 1 - Built-In Pythoner"

        return "Unknown Configuration"

    if not trigger:
        return "", "", "", ""

    python_modules_path = os.path.join(os.path.dirname(__file__), '')
    project_directory = os.path.abspath(os.path.join(python_modules_path, os.pardir))
    executable_path = os.path.normpath(sys.executable)

    # Print Environment Information
    print("* * * * * * * * * * * * * * * * * * * * *")
    print("")
    print("*** Project and Python Info ****")
    print("")
    print("--> Isadora Project Paths")
    print("Project Directory:", project_directory)
    print("Python Modules Path:", python_modules_path)
    print("")
    print("--> Active User")
    print("os Current User:", os.getlogin())
    print("getpass Current User:", getpass.getuser())
    print("")
    print("--> Python Details")
    print("Python Version (active):", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("Python Executable Path:", executable_path)
    print("")
    
    # Detect Pythoner configuration
    config_option = detect_pythoner_config(executable_path, project_directory)
    print("Pythoner Environment Configuration:", config_option)
    print("")
    print("* * * * * * * * * * * * * * * * * * * * *")

    return executable_path, python_modules_path, project_directory, config_option

# python_finalize is called just before the actor is deactivated
def python_finalize():
    return

if __name__ == '__main__':
    """
    This section is for IDE testing only and will NOT run inside Isadora.
    It helps you validate the script externally. Ensure your IDE uses the
    same Python version and VENV as Isadora.
    """
    # Simulate a trigger input
    values = python_main(True)
    print("Returned values:", values)
