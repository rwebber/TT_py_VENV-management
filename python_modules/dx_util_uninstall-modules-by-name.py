"""A script to uninstall specified Python modules from a virtual environment.

This program processes a trigger and a list of module names, determines the
appropriate virtual environment, and uses pip to uninstall the requested
modules. It supports multiple module names via a comma-separated list and
generates detailed status messages regarding successes or failures during
uninstallation.
"""

# Enter the name as required by PIP to uninstall the requested module.
# Check https://pypi.org/ for module details.
# Supports multiple comma separated names.

import os
import subprocess
import platform

# iz_input 1 "Uninstall Trigger"
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

    # Determine pip path for the virtual environment
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        creationflags = subprocess.CREATE_NO_WINDOW
    elif platform.system() == "Darwin":
        pip_path = os.path.join(venv_path, "bin", "pip")
        creationflags = 0
    else:
        return "Unsupported OS."

    # Check if pip exists
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
                [pip_path, "uninstall", "-y", module],
                capture_output=True,
                text=True,
                creationflags=creationflags
            )
            if result.returncode == 0:
                results.append(f"✓ {module} uninstalled.")
            else:
                # Check if it's already not installed
                if "not installed" in result.stdout.lower():
                    results.append(f"✓ {module} was already not installed.")
                else:
                    results.append(f"✗ {module} failed:\n{result.stderr.strip()}")
        except Exception as e:
            results.append(f"✗ {module} exception:\n{e}")

    return "\n".join(results)
