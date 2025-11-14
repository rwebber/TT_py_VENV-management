import os
import sys
import importlib

# iz_input 1 "trigger"
# iz_input 2 "starting_path"
# iz_output 1 "folder_path"


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


def python_init(trigger, start):
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


def python_main(trigger, start_path):
    """
    Uses the get_folder_from_selection_dialog function to get a selected folder path.
    Outputs the selected folder path or a message if no folder was selected.
    """
    if trigger:
        # folder_path = dsh.get_folder_from_selection_dialog(start_path)
        folder_path = dsh.get_folder_from_selection_dialog()
        return folder_path
    return "No action taken"


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
    trig = True  # Simulate trigger activation
    starting_path = "/Users"  # Example starting path
    print(python_init(trig, starting_path))  # Run initialization and open folder dialog
    python_finalize()  # Finalize tasks


