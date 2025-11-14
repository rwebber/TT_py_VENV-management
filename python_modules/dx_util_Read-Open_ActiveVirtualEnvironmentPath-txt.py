"""
Processes and manages virtual environment files and interactions, including validation,
creation, and file handling.

This script provides utilities to handle operations related to Python virtual environments,
including fallback definitions when external dependencies are not available. It also offers
a mechanism to interact with an ActiveVirtualEnvironmentPath configuration file for various
trigger-based actions.
"""

import os
import sys
import importlib

# iz_input 1 "Read Trigger"
# iz_input 2 "Open Trigger"
# iz_output 1 "Venv Path"


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


def python_init(read_trigger, open_trigger):
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


def python_main(read_trigger, open_trigger):
    """
    Reads the content of ActiveVirtualEnvironmentPath.txt and outputs it or opens it in the default text editor.

    Args:
    read_trigger (bool): Trigger to read and output the file content.
    open_trigger (bool): Trigger to open the file in the default editor.

    Returns:
    str: The path stored in ActiveVirtualEnvironmentPath.txt when read_trigger is activated.
    """
    # Get the file path for ActiveVirtualEnvironmentPath.txt
    file_path = dsh.get_active_virtualenv_path()

    # Read and output the file content
    if read_trigger:
        success, result = dsh.read_file(file_path)
        return result if success else result  # Return either the content or error message

    # Open the file in the default text editor
    if open_trigger:
        success, result = dsh.open_file_in_editor(file_path)
        return result  # Return the result message

    return


def python_finalize():
    """
    Finalizes the script by performing any cleanup tasks.
    This function is called when the script is deactivated in Pythoner.
    """

    # # Remove dx_system_helpers from sys.modules to ensure it is reloaded next time
    # if 'dx_system_helpers' in sys.modules:
    #     del sys.modules['dsh']

    # Remove dx_system_helpers from sys.modules to ensure it is reloaded next time
    if dsh.__name__ in sys.modules:
        del sys.modules[dsh.__name__]

if __name__ == '__main__':
    # Simulate trigger inputs for testing
    print(python_main(True, False))  # Test reading and outputting the file content
    # print(python_main(False, True))  # Test opening the file in the default editor (uncomment to test)
