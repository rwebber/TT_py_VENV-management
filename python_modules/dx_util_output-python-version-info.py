import sys
import platform

# iz_input 1 "Trigger"
# iz_output 1 "sys.version"
# iz_output 2 "platform.python_version"

def python_init(trigger):
    """
    Initialize the script. Returns the project root path if triggered.
    Note: Ensure the number of parameters here matches python_main().
    """
    return "init","init"


def python_main(trigger):
    if not trigger:
        return

    return [
        sys.version,
        platform.python_version()
    ]