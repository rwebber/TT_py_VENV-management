"""
Handles virtual environment-related operations such as creation, validation, and
package management. Provides fallback implementations for `dx_system_helpers`
functions and defines the main application logic for generating a `requirements.txt`
file.

This module also contains utilities for interacting with virtual environments and
ensures compatibility when `dx_system_helpers` is not available.
"""

import os
import sys
import importlib

# iz_input 1 "Trigger"
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


def python_init(izzyTrigger):
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


def python_main(izzyTrigger):
    """
    Generates a requirements.txt file listing all installed Python packages,
    excluding those in the bad-list.

    Args:
    izzyTrigger (bool): A trigger input to start the script execution.

    Returns:
    str: Status message indicating the outcome of the operation.
    """

    # List of packages to exclude from requirements.txt
    bad_list = ['pip', 'virtualenv']

    # Determine the file path for requirements.txt in the project directory
    project_directory = dsh.get_project_directory()
    filepath = os.path.join(project_directory, 'requirements.txt')

    if izzyTrigger:
        # Execute pip list and handle errors
        success, result = dsh.execute_pip_list()
        if not success:
            return result  # Return error message from execute_pip_list

        # Prepare the content for requirements.txt, excluding packages in bad_list
        content_lines = []
        for line in result.splitlines()[2:]:  # Skip header lines
            package, version = line.split()[:2]
            if package.lower() not in bad_list:
                content_lines.append(f"{package}=={version}\n")

        # Write to requirements.txt and handle errors
        success, message = dsh.write_to_file(filepath, content_lines)
        return message

    return "Script did not run. Trigger not activated."


def python_finalize():
    """
    Finalization logic for the script.
    """
    print("Script finalizing...")

    # Remove dx_system_helpers from sys.modules to ensure it is reloaded next time
    if dsh.__name__ in sys.modules:
        del sys.modules[dsh.__name__]


if __name__ == '__main__':
    # This block is for testing the script in an IDE
    print(python_main(True))