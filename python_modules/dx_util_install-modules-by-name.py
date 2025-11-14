"""
Provides functionality to install specified Python modules inside a virtual environment.

This module detects the platform-specific path of the `pip` executable within a virtual
environment and installs user-specified modules using it when triggered. It supports
error handling for invalid module names and unsupported operating systems.

Functions:
    python_main(trigger, module_list): Executes module installation based on input trigger
    and provided module list.

"""

# Enter the name as required by PIP to install the requested module.
# Check https://pypi.org/ for module details.
# Supports multiple comma separated names.
# The default 'opencv-python, numpy' will provide essentials for supporting video IO in Pythoner.

import os
import subprocess
import platform

# iz_input 1 "Install Trigger"
# iz_input 2 "Module List"
# iz_output 1 "Status"


def python_init(trigger, module_list):
    return "init"


def python_main(trigger, module_list):
    if not trigger or not module_list:
        return "Waiting for trigger and module list..."

    # Determine project root and venv path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    venv_path = os.path.join(project_root, "Virtual_Env")

    # Locate pip in the venv (platform-specific)
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        creationflags = subprocess.CREATE_NO_WINDOW
    elif platform.system() == "Darwin":
        pip_path = os.path.join(venv_path, "bin", "pip")
        creationflags = 0
    else:
        return "Unsupported OS."

    if not os.path.isfile(pip_path):
        return f"pip not found at:\n{pip_path}\nIs this a valid virtual environment?"

    # Parse and sanitize module list
    modules = [m.strip() for m in module_list.split(',') if m.strip()]
    if not modules:
        return "No valid module names provided."

    results = []

    for module in modules:
        try:
            result = subprocess.run(
                [pip_path, "install", module],
                capture_output=True,
                text=True,
                creationflags=creationflags
            )
            if result.returncode == 0:
                results.append(f"✓ {module} installed.")
            else:
                results.append(f"✗ {module} failed:\n{result.stderr.strip()}")
        except Exception as e:
            results.append(f"✗ {module} exception:\n{e}")

    return "\n".join(results)
