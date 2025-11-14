"""
Handles virtual environment path updates based on the specified trigger.

This module updates the active virtual environment path used by the system,
based on the user-provided input and trigger. It performs necessary file
operations to persist the provided path and ensures required directories
exist.

Functions:
    python_main(virtual_env_path, trigger): Updates the active virtual
    environment path if a trigger is activated and a valid path is
    provided.
"""

import os

# iz_input 1 "Virtual Environment Path"
# iz_input 2 "Trigger"
# iz_output 1 "Status Message"

def python_main(virtual_env_path, trigger):
    if not trigger:
        return "Waiting for trigger."

    if not virtual_env_path:
        return "Error: No virtual environment path provided."

    if os.name == 'nt':
        active_env_file_path = r'C:\Program Files\Common Files\TroikaTronix\Python\ActiveVirtualEnvironmentPath.txt'
    else:
        active_env_file_path = '/Library/Application Support/TroikaTronix/Python/ActiveVirtualEnvironmentPath.txt'

    try:
        os.makedirs(os.path.dirname(active_env_file_path), exist_ok=True)
        with open(active_env_file_path, 'w') as file:
            file.write(virtual_env_path.strip())

        return f"Active VENV path updated: {virtual_env_path.strip()}"

    except IOError as e:
        return f"IOError: {str(e)}"
