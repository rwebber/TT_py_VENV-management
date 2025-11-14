"""
Helpers for managing Python virtual environments and integration with the dx_system_helpers module.

This module provides fallback implementations of several utility functions from the
dx_system_helpers module for virtual environment management. It also includes the
main script functions for initialization, main logic, and cleanup tasks during script execution.
"""

import os
import sys
import importlib

# iz_output 1 "Project Directory"
# iz_output 2 "Active Virtual Environment Path"
# iz_output 3 "Pip Path"

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
    Collects important paths (e.g., project directory, pip path) and outputs them
    directly as named outputs for Pythoner.
    """

    if not izzyTrigger: # allow to run only on Trigger
        return None

    # Collect paths
    project_directory = dsh.get_project_directory()
    active_virtualenv_path = dsh.get_active_virtualenv_path()
    pip_path = dsh.get_pip_path(project_directory)

    # Output paths directly to Pythoner outputs
    return project_directory, active_virtualenv_path, pip_path

def python_finalize():
    """
    Finalizes the script by performing any cleanup tasks.
    This function is called when the script is deactivated in Pythoner.
    """
    print("Script finalizing...")

    # Remove dx_system_helpers from sys.modules to ensure it is reloaded next time
    if dsh.__name__ in sys.modules:
        del sys.modules[dsh.__name__]

if __name__ == '__main__':
    """
    This section allows the script to be run and tested in an IDE.
    It will not execute within the Pythoner plugin in Isadora.
    """
    project_directory, active_virtualenv_path, pip_path = python_init()  # Run initialization and output paths
    print(f"Project Directory: {project_directory}")
    print(f"Active Virtual Environment Path: {active_virtualenv_path}")
    print(f"Pip Path: {pip_path}")
    python_finalize()  # Finalize tasks
