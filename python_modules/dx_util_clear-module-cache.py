"""
Provides functions to manage and clear cached Python modules from a specific directory.

This module is specifically designed to work with a Python development environment, particularly
use cases involving Pythoner and dynamic module reloading during development. It provides a clean
start by clearing specified user modules, avoiding inadvertently running outdated code.

Functions:
    python_init: Initializes and indicates readiness for module clearing.
    python_main: Clears cached user modules loaded from a specific folder and returns status.
    python_finalize: Finalizes the module with no explicit action.
"""


# This function is VERY important when you are developing Pythoner projects that link files in the python_modules folder.
# This external files are cached by Python, and often will not be reloaded.
# This leads to code running that isn't uptodate (may have been updated via external editor).
# Triggering this function, removes all cached modules from Pythoner.
# Recommended usecase - Use this function in a separate scene from your Pythoner development.
# This separation ensures a clean start, and allows the INIT functions to load specified modules.

import sys
import os

# iz_input 1 "trigger"
# iz_output 1 "status"

def python_init(trigger):
    return "init"

def python_main(trigger):
    if trigger:
        # Get the base path of your document's python_modules folder
        try:
            base_path = os.path.join(os.path.dirname(__file__), '..', 'python_modules')
        except:
            return "Error determining base path"

        cleared = []
        for name, module in list(sys.modules.items()):
            try:
                # Only clear modules that were loaded from your python_modules folder
                if hasattr(module, '__file__') and module.__file__ and os.path.abspath(base_path) in os.path.abspath(module.__file__):
                    del sys.modules[name]
                    cleared.append(name)
            except Exception as e:
                continue  # Some built-ins may throw during this check

        return f"Cleared: {cleared}" if cleared else "No user modules cleared"
    return "No action"

def python_finalize():
    return

if __name__ == '__main__':
    # IDE-friendly section. Not run in Isadora.
    python_init(0)
    print(python_main(True))
    python_finalize()
