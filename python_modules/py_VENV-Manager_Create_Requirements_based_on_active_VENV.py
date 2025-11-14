"""
A module to generate a requirements.txt file listing all installed Python packages.

This script generates a file excluding certain packages (e.g., build tools) and
adds metadata such as Python version, platform, and timestamp. It is optimized
to operate only when triggered.

Functions:
    python_main: Main function to execute the requirements file creation process.
"""

import subprocess
import sys
import os
import platform
from datetime import datetime

# iz_input 1 "Trigger"
# iz_output 1 "Status Message"

def python_main(izzyTrigger):
    """
    Generates a requirements.txt file listing all installed Python packages,
    excluding those in the bad-list, and includes helpful header comments
    with Python version, platform, and timestamp.

    Args:
    izzyTrigger (bool): A trigger input to start the script execution.

    Returns:
    str: Status message indicating the outcome of the operation.
    """

    bad_list = ['pip', 'virtualenv', 'setuptools', 'wheel'] # will be added by virtualenv
    python_modules_path = os.path.join(os.path.dirname(__file__), '')
    project_directory = os.path.abspath(os.path.join(python_modules_path, os.pardir))
    filepath = os.path.join(project_directory, 'requirements.txt')

    if izzyTrigger:
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE)

            if result.returncode != 0:
                return "Error in running pip list: " + result.stderr

            python_version = platform.python_version()
            platform_info = f"{platform.system()} {platform.release()}"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                with open(filepath, 'w') as f:
                    # Write header comments
                    f.write(f"# Created with Pythoner running Python version {python_version}\n")
                    f.write(f"# Created on platform {platform_info}\n")
                    f.write(f"# Timestamp: {timestamp}\n")
                    for line in result.stdout.splitlines()[2:]:  # Skip pip list header
                        package, version = line.split()[:2]
                        if package.lower() not in bad_list:
                            f.write(f"{package}=={version}\n")
                return "requirements.txt created at " + filepath
            except IOError as e:
                return "IOError: Failed to write to file: " + str(e)
        except subprocess.SubprocessError as e:
            return "SubprocessError: Failed to run subprocess: " + str(e)

    return "Script did not run. Trigger not activated."

if __name__ == '__main__':
    # This section runs only in an IDE and is ignored by Pythoner
    print(python_main(True))
