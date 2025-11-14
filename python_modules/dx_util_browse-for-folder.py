"""
This module provides functions for opening a folder selection dialog across
various platforms (Windows, macOS) and a main entry point for platform-based
execution. The functionality handles platform-specific folder browsing
and interaction.

Functions:
    - browse_windows_folder: Opens a folder selection dialog on Windows
      systems.
    - browse_macos_folder: Opens a folder selection dialog on macOS
      systems using AppleScript.
    - python_main: Serves as the main entry point to execute platform-specific
      folder browsing or provide fallback instructions for other systems.
"""

"""
Copyright (c) 2025 Ryan Webber for TroikaTronix
Licensed under the MIT License (see below for terms)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

THE ABOVE COPYRIGHT NOTICE AND THIS PERMISSION NOTICE SHALL BE INCLUDED IN
ALL COPIES OR SUBSTANTIAL PORTIONS OF THE SOFTWARE.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import sys
import ctypes
from ctypes import wintypes
import subprocess

# iz_input 1 "Open Browser (Trigger)"
# iz_output 1 "Selected Path or Message"

def browse_windows_folder():
    BIF_RETURNONLYFSDIRS = 0x00000001
    BIF_NEWDIALOGSTYLE = 0x00000040

    class BROWSEINFO(ctypes.Structure):
        _fields_ = [
            ("hwndOwner", wintypes.HWND),
            ("pidlRoot", ctypes.c_void_p),
            ("pszDisplayName", ctypes.c_wchar_p),
            ("lpszTitle", ctypes.c_wchar_p),
            ("ulFlags", ctypes.c_uint),
            ("lpfn", ctypes.c_void_p),
            ("lParam", ctypes.c_void_p),
            ("iImage", ctypes.c_int),
        ]

    display_name_buffer = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    path_buffer = ctypes.create_unicode_buffer(wintypes.MAX_PATH)

    ctypes.windll.ole32.CoInitialize(None)

    bi = BROWSEINFO()
    bi.hwndOwner = None
    bi.pidlRoot = None
    bi.pszDisplayName = ctypes.cast(display_name_buffer, ctypes.c_wchar_p)
    bi.lpszTitle = "Select Folder for Virtual Environment"
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE
    bi.lpfn = None
    bi.lParam = None
    bi.iImage = 0

    SHBrowseForFolder = ctypes.windll.shell32.SHBrowseForFolderW
    SHGetPathFromIDList = ctypes.windll.shell32.SHGetPathFromIDListW

    pidl = SHBrowseForFolder(ctypes.byref(bi))

    if pidl:
        SHGetPathFromIDList(pidl, path_buffer)
        ctypes.windll.ole32.CoTaskMemFree(pidl)
        return path_buffer.value
    else:
        return ""

def browse_macos_folder():
    try:
        script = '''
        set selectedFolder to POSIX path of (choose folder with prompt "Select Folder for Virtual Environment")
        return selectedFolder
        '''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "No folder selected."
    except Exception as e:
        return f"Error: {str(e)}"

def python_main(trigger):
    if not trigger:
        return

    if sys.platform.startswith('win'):
        path = browse_windows_folder()
        return path if path else "No folder selected."
    elif sys.platform.startswith('darwin'):
        return browse_macos_folder()
    elif sys.platform.startswith('linux'):
        return "Linux detected: Please enter folder path manually."
    else:
        return f"Unsupported platform: {sys.platform}"

# Uncomment to test standalone
# print(python_main(True))
