"""
This module provides Python utilities for validating package dependencies
listed in a requirements.txt file through communication with the PyPI API. It
checks if specified versions exist and whether compatible wheels are available
for the current platform.
"""

# TODO: handle case without internet access

import os
import re
import json
import urllib.request
import urllib.error
import ssl
import sys, importlib
# from packaging import tags  # we use module injection to allow us to use this without installing this module

# iz_input 1 "project_path"
# iz_input 2 "trigger"
# iz_output 1 "status"


packaging = None
tags = None
PLATFORM_TAGS = []


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


def python_init(project_path, trigger):
    global packaging, tags, PLATFORM_TAGS
    mName = "packaging"
    try:
        packaging = import_injected(mName, strict=True)
        # import importlib
        # from packaging import tags
        tags = importlib.import_module("packaging.tags")
        PLATFORM_TAGS = [str(t) for t in tags.sys_tags()]
        return "init"
    except RuntimeError:
        print("Unable to load injected module: " + mName)
        # or: print(f"Unable to load injected module: {mName}")
        packaging = tags = None
        PLATFORM_TAGS = []
        return "INIT error"


# Use system default SSL context
default_context = ssl.create_default_context()

# Precompute platform tags for wheel compatibility checking
# PLATFORM_TAGS = [str(tag) for tag in tags.sys_tags()]
# print("Platform tags (first 5):", PLATFORM_TAGS[:5])  # For debugging


def python_main(project_path, trigger):
    """
    Validates versions listed in requirements.txt using PyPI API.
    Checks if version exists AND if a compatible wheel is available.
    """
    if not PLATFORM_TAGS:
        return "packaging not available"

    if not trigger:
        return "Waiting for Trigger"

    # Construct path to requirements.txt
    req_path = os.path.join(project_path, 'requirements.txt')
    if not os.path.isfile(req_path):
        return f"Error: requirements.txt not found at {req_path}"

    status_messages = []
    with open(req_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            match = re.match(r'^([a-zA-Z0-9_\-]+)==([\d\.]+)$', line)
            if not match:
                status_messages.append(f"⚠️ Unrecognized format: {line}")
                continue

            pkg, version = match.groups()
            url = f"https://pypi.org/pypi/{pkg}/json"
            data = None
            ssl_warning = False

            try:
                with urllib.request.urlopen(url, context=default_context) as response:
                    data = json.load(response)

            except urllib.error.URLError as e:
                if isinstance(e.reason, ssl.SSLError):
                    try:
                        insecure_context = ssl._create_unverified_context()
                        with urllib.request.urlopen(url, context=insecure_context) as response:
                            data = json.load(response)
                            ssl_warning = True
                    except Exception as fallback_error:
                        status_messages.append(f"❌ SSL error checking {pkg}: {fallback_error}")
                        continue
                else:
                    status_messages.append(f"❌ URLError checking {pkg}: {e}")
                    continue

            except Exception as e:
                status_messages.append(f"❌ Error checking {pkg}: {e}")
                continue

            # Analyze result
            if data:
                available = data.get("releases", {}).keys()
                if version in available:
                    # Check wheel compatibility
                    releases = data.get("releases", {}).get(version, [])
                    wheels = [r for r in releases if r["filename"].endswith(".whl")]

                    compatible = False
                    for wheel in wheels:
                        filename = wheel["filename"].lower()
                        if any(tag.lower() in filename for tag in PLATFORM_TAGS):
                            compatible = True
                            break

                    if compatible:
                        msg = f"✅ {pkg}=={version} is available and compatible"
                    elif wheels:
                        msg = f"⚠️ {pkg}=={version} exists but has NO compatible wheel for this platform"
                    else:
                        msg = f"⚠️ {pkg}=={version} exists but only as source (no wheels)"

                else:
                    latest = sorted(available)[-1] if available else "N/A"
                    msg = f"❌ {pkg}=={version} not found (latest: {latest})"

                if ssl_warning:
                    msg += " (SSL fallback used)"

                status_messages.append(msg)

    return "\n".join(status_messages) if status_messages else "✅ All entries valid."

def python_finalize():
    """
    Called when Pythoner actor is deactivated.
    """
    pass

if __name__ == '__main__':
    # For external testing
    test_path = r"/your/project/path"
    print(python_main(test_path, True))
    python_finalize()
