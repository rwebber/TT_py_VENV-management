import os
import platform
import subprocess

# iz_input 1 "open_trigger"
# iz_input 2 "folder_path"
# iz_output 1 "result"

def open_folder(folder_path):
    """
    Opens a folder in the default file explorer (Explorer for Windows, Finder for macOS).

    Args:
        folder_path (str): Path to the folder to open.

    Returns:
        tuple: (bool, str) Success status and message.
    """
    try:
        if not os.path.isdir(folder_path):
            return False, f"Path is not a valid directory: {folder_path}"

        current_platform = platform.system()
        if current_platform == "Windows":
            os.startfile(folder_path)  # Opens folder in Windows Explorer
        elif current_platform == "Darwin":
            subprocess.run(["open", folder_path], check=True)  # Opens folder in macOS Finder
        elif current_platform == "Linux":
            subprocess.run(["xdg-open", folder_path], check=True)  # Opens folder in default file manager for Linux
        else:
            return False, f"Unsupported platform: {current_platform}"

        return True, f"Folder opened successfully: {folder_path}"
    except Exception as e:
        return False, f"Error opening folder: {str(e)}"


# python_main is called whenever an input value changes
def python_main(open_trigger, folder_path):
    """
    Main function to handle folder opening based on trigger.

    Args:
        open_trigger (bool): Trigger to open the folder.
        folder_path (str): Path to the folder to open.

    Returns:
        str: Result message.
    """
    if open_trigger:
        success, result = open_folder(folder_path)
        return result  # Return success or error message
    return "No action triggered."


if __name__ == '__main__':
    """
    This section allows testing outside Pythoner. It will not run in Pythoner.
    """
    # Simulate inputs
    open_trigger = True
    folder_path = r"D:\OneDrive\Documents\_Troikatronix\TT_izzy VENV management"

    # Run test
    output = python_main(open_trigger, folder_path)
    print("Output:", output)
