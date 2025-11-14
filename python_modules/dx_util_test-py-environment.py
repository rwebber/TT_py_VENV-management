"""
Module to check the presence and validity of Python virtual environments.

This module verifies the existence of a virtual environment by inspecting
the Python executable and its parent directory structure. It includes
functions to initialize, execute, and finalize the process for environment
verification.
"""

import os
import sys


# iz_input 1 "trigger"
# iz_output 1 "venv_status"

# def python_init(trigger):
# return check_venv_exists()

def python_main(trigger):
    if trigger:
        return check_venv_exists()


def check_venv_exists():
    """
    Check if the Python executable and its parent folders still exist.
    """
    python_path = sys.executable
    venv_root = os.path.dirname(os.path.dirname(python_path))  # Up two levels: from .../Scripts/python.exe to venv root
    print("Checking environment - Python path:", python_path)
    print("Checking environment - VENV root:", venv_root)

    if os.path.isdir(venv_root) and os.path.isfile(python_path):
        print("Checking environment - VENV is OK")
        return "VENV OK"
    else:
        print("Checking environment - VENV is MISSING")
        return "VENV MISSING"


def python_finalize():
    return


if __name__ == '__main__':
    # This block is for testing outside Isadora in an IDE with matching Python version
    print(python_init(True))
    print(python_main(True))
    python_finalize()
