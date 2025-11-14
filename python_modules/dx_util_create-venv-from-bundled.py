"""A module to manage the creation of a virtual environment using an embedded Python executable.

This module ensures the setup of a Virtual_Env directory within the project root
using the embedded Python bundled with Pythoner. The functionality targets
different operating systems (Windows and macOS) to initialize and manage the
virtual environment required for the project.

Functions:
    python_init(trigger): Initializes the actor upon activation.
    python_main(trigger): Ensures the virtual environment is created and ready for use.
"""

# Creates Virtual_Env if it doesn't exist yet and creates VENV in this folder
# using the embedded python that is bundled with Pythoner.
# Pythoner will 'see' this folder on startup and use this local VENV for the project.

import os
import subprocess
import platform
import glob

# iz_input 1 "Trigger"
# iz_output 1 "Status"

# python_init is called when the actor is first activated
def python_init(trigger):
    return "init"


# python_finalize is called just before the actor is deactivated
# def python_finalize():
#     return


# ---------- helpers ----------

def _is_windows():
    return platform.system() == "Windows"

def _venv_exists(path: str) -> bool:
    """Detect an existing/usable venv by presence of pyvenv.cfg and Scripts/bin."""
    if not os.path.isdir(path):
        return False
    if not os.path.isfile(os.path.join(path, "pyvenv.cfg")):
        return False
    scripts_dir = os.path.join(path, "Scripts" if _is_windows() else "bin")
    return os.path.isdir(scripts_dir) and os.path.isfile(
        os.path.join(scripts_dir, "python.exe" if _is_windows() else "python")
    )

def _run(cmd, creationflags=0):
    return subprocess.run(cmd, capture_output=True, text=True, creationflags=creationflags)

def _ensure_windows_dlls_folder(embedded_python: str):
    """
    On Windows, make sure a DLLs folder exists beside the embedded python.exe.
    Some virtualenv steps probe for DLLs; creating it avoids path errors.
    """
    if not _is_windows():
        return None
    base_dir = os.path.dirname(embedded_python)
    dlls_path = os.path.join(base_dir, "DLLs")
    if not os.path.exists(dlls_path):
        try:
            os.makedirs(dlls_path)
            # keep return None to avoid cluttering Isadora Monitor
        except Exception as e:
            return f"Warning: Could not create DLLs folder at {dlls_path}: {e}"
    return None

def _ensure_stdlib_for_embedded_windows(embedded_python: str, venv_path: str):
    """
    On Windows, Pythoner's embedded build ships a stdlib folder (e.g., python310/)
    and no python310.zip. The venv's python.exe may not find 'encodings' unless we
    tell it where to look. Create pythonXY._pth next to the venv python.exe that
    points at the embedded stdlib folder.
    """
    if not _is_windows():
        return None  # not needed on macOS

    base = os.path.dirname(embedded_python)
    scripts = os.path.join(venv_path, "Scripts")
    if not os.path.isdir(scripts):
        return "Warning: venv Scripts folder not found."

    # Find python3XY stdlib folder beside embedded python (e.g., python310)
    candidates = [p for p in glob.glob(os.path.join(base, "python3*")) if os.path.isdir(p)]
    if not candidates:
        return "Warning: No stdlib folder (python3XY) found beside embedded Python."

    stdlib_dir = candidates[0]
    ver_suffix = os.path.basename(stdlib_dir).replace("python", "")  # -> "310", "311", etc.
    pth_path = os.path.join(scripts, f"python{ver_suffix}._pth")

    try:
        with open(pth_path, "w", encoding="utf-8") as f:
            # absolute path to stdlib folder, then current dir, then enable site
            f.write(stdlib_dir + "\n.\nimport site\n")
        return None
    except Exception as e:
        return f"Warning: Could not write {os.path.basename(pth_path)}:\n{e}"

def _health_check(venv_path: str, creationflags=0):
    """Smoke test that the venv can import encodings and report its version."""
    py = os.path.join(venv_path, "Scripts" if _is_windows() else "bin",
                      "python.exe" if _is_windows() else "python")
    try:
        r = _run([py, "-c", "import encodings, sys; print('OK', sys.version)"], creationflags)
        return r.returncode == 0, (r.stdout or r.stderr).strip()
    except Exception as e:
        return False, str(e)


# ---------- main ----------

def python_main(trigger):
    if not trigger:
        return

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    venv_path = os.path.join(project_root, "Virtual_Env")

    if _is_windows():
        embedded_python = r"C:\Program Files\Common Files\TroikaTronix\Isadora Plugins\Pythoner.izzyplug\python.exe"
        creationflags = subprocess.CREATE_NO_WINDOW
    elif platform.system() == "Darwin":
        embedded_python = "/Library/Application Support/TroikaTronix/Isadora Plugins/Pythoner.izzyplug/python"
        creationflags = 0
    else:
        return "Unsupported OS."

    if not os.path.isfile(embedded_python):
        return f"Embedded Python not found at:\n{embedded_python}"

    # Ensure a DLLs folder exists beside the embedded interpreter (Windows only)
    warn_dlls = _ensure_windows_dlls_folder(embedded_python)

    # Ensure target folder exists
    try:
        os.makedirs(venv_path, exist_ok=True)
    except Exception as e:
        return f"Cannot create target folder:\n{venv_path}\n{e}"

    # If already a venv, short-circuit
    if _venv_exists(venv_path):
        ok, msg = _health_check(venv_path, creationflags)
        base = f"Virtual environment already present:\n{venv_path}\nHealth: {'OK' if ok else 'FAIL'}{(' - ' + msg) if msg else ''}"
        if warn_dlls:
            base += "\n" + warn_dlls
        return base

    # Build the environment using Pythoner's embedded interpreter (no downloads)
    cmd = [
        embedded_python, "-m", "virtualenv",
        "--copies",
        "--no-download",
        "--python", embedded_python,
        venv_path
    ]

    try:
        result = _run(cmd, creationflags)
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()

        if result.returncode != 0:
            details = "\n".join(s for s in [stderr, stdout] if s)
            return "virtualenv failed:\n" + (details if details else f"exit code {result.returncode}")

        # Windows: ensure stdlib is discoverable (pythonXY._pth pointing to Pythoner's pythonXY/)
        warn_stdlib = _ensure_stdlib_for_embedded_windows(embedded_python, venv_path)

        # Health check: can the venv import encodings and run?
        ok, msg = _health_check(venv_path, creationflags)
        base_report = f"Virtual environment created at:\n{venv_path}\nHealth: {'OK' if ok else 'FAIL'}{(' - ' + msg) if msg else ''}"
        if warn_dlls:
            base_report += "\n" + warn_dlls
        if warn_stdlib:
            base_report += "\n" + warn_stdlib
        if stdout and not ok:
            base_report += "\n" + stdout
        if not ok and stderr:
            base_report += "\n" + stderr
        return base_report

    except Exception as e:
        return f"Exception during virtualenv creation:\n{e}"
