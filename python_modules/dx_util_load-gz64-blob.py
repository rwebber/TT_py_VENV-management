"""
This module provides functionality to process a gz64-encoded .txt file,
normalize its path and format its content into a JSON list string representation
while ensuring proper text decoding and cleanup.
"""

# iz_input 1 "file_path"    # Local path to gz64 .txt file (relative to Pythoner root or absolute)
# iz_input 2 "trigger"      # Triggers execution
# iz_output 1 "json_blob"   # Formatted JSON list string

import os, json

# python_init (not used in this case)
def python_init(file_path, trigger):
    return

# Main logic
def python_main(file_path, trigger):
    if not trigger:
        return ""

    try:
        # Normalize path (can be relative to Pythoner working dir or absolute)
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.path.dirname(__file__), file_path)

        with open(file_path, "rb") as f:
            raw = f.read()

        # Remove BOMs and decode to str
        for bom in [b'\xef\xbb\xbf', b'\xff\xfe', b'\xfe\xff']:
            if raw.startswith(bom):
                raw = raw[len(bom):]

        text = raw.decode("utf-8", errors="ignore")

        # Clean and pack into JSON string
        clean_blob = text.strip().replace("\r", "").replace("\n", "")
        json_list = json.dumps([clean_blob])  # this ensures escaping is correct

        return json_list

    except Exception as e:
        return f"ERROR: {e}"

# Cleanup (not needed)
def python_finalize():
    return


# External editor testing block
if __name__ == '__main__':
    """ 
    This section is for IDE development only — not run inside Pythoner.
    Make sure your file path is accurate and you use the same Python version as Pythoner.
    """
    test_file = "python_modules/dx_helpers_gz64.txt"
    print(python_main(test_file, True))
