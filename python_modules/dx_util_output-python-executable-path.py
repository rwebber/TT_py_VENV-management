import sys, os  # Required to access system-specific parameters and functions

# iz_input 1 "trigger"
# iz_output 1 "python_exe_path"

""" 
Define any Globals here, if needed in future
"""


# python_init is called when the actor is first activated.
# It requires the same number of parameters input as python_main()
def python_init(trigger):
    """
    Initialize the script. Returns the project root path if triggered.
    Note: Ensure the number of parameters here matches python_main().
    """
    return "init"


# python_main is called whenever an input value changes
def python_main(trigger):
    # Return the path to the current python executable
    if trigger:
        return os.path.normpath(sys.executable)
    return


# python_finalize is called just before the actor is deactivated
def python_finalize():
    # Use this section to clean up resources if needed
    return
