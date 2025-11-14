"""
A program to process and adjust a `requirements.txt` file by relaxing version constraints and
creating a backup of the original file.

The program updates package versions in the format `pkg==X.Y.Z` to `pkg<=X.Y.Z` in the
`requirements.txt` file at the specified project path, if triggered. It also handles file
backup and overwriting.

Functions:
    python_main: Primary function to process `requirements.txt` file.
    python_init: Initialization function (currently not implemented).
    python_finalize: Finalization function (currently not implemented).
"""

import os
import re
import shutil

# iz_input 1 "project_path"
# iz_input 2 "trigger"
# iz_output 1 "status"

def python_main(project_path, trigger):
    if not trigger:
        return 0

    req_path = os.path.join(project_path, 'requirements.txt')
    backup_path = os.path.join(project_path, 'original_requirements.txt')

    if not os.path.isfile(req_path):
        print(f"❌ requirements.txt not found at: {req_path}")
        return 0

    try:
        # Backup the original
        shutil.copy(req_path, backup_path)
        print(f"✅ Backed up original to: {backup_path}")

        relaxed_lines = []
        with open(req_path, 'r') as file:
            for line in file:
                stripped = line.strip()
                match = re.match(r'^([a-zA-Z0-9_\-]+)==([\d\.]+)$', stripped)
                if match:
                    pkg, version = match.groups()
                    relaxed_line = f"{pkg}<={version}"
                    relaxed_lines.append(relaxed_line)
                    print(f"⬇ Relaxed: {line.strip()} → {relaxed_line}")
                else:
                    relaxed_lines.append(line.rstrip())

        # Write updated file
        with open(req_path, 'w') as file:
            file.write('\n'.join(relaxed_lines) + '\n')

        print("✅ requirements.txt rewritten successfully.")
        return 1

    except Exception as e:
        print(f"❌ Error updating requirements.txt: {e}")
        return 0

def python_init(project_path, trigger):
    return

def python_finalize():
    return

if __name__ == '__main__':
    print(python_main("/your/project/path", True))
