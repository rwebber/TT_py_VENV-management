import pkgutil

# iz_input 1 "Trigger"
# iz_output 1 "Installed Modules (list)"

def python_init(trigger):
    """
    Initialize the script. Returns the project root path if triggered.
    Note: Ensure the number of parameters here matches python_main().
    """
    return "init"


def python_main(trigger):
    if not trigger:
        return

    modules = sorted({module.name for module in pkgutil.iter_modules()})
    return ', '.join(modules)  # Returns comma-separated list of available modules
