import subprocess
import os
import re
import platform

# iz_input 1 "Venv Folder Name"          # optional; defaults to "Virtual_Env" if blank
# iz_input 2 "Filepath for Venv Creation" # optional; defaults to <project_root> if blank
# iz_input 3 "Use Requirements"           # 0/1 (False/True)
# iz_input 4 "Trigger"
# iz_output 1 "Status Message"


"""
Unified Virtual Environment Creator for Isadora Pythoner
--------------------------------------------------------

This script creates and initializes a Python virtual environment (venv)
using the embedded Python runtime included with the Pythoner plugin.
It is designed to work on both Windows and macOS and combines the
functionality of the two previous scripts into one unified version.

USE CASES
==========

1. **Project-local mode (simple / Version 1)**
   - Automatically creates a virtual environment in:
       <project_root>/Virtual_Env
   - Does **not** install packages from requirements.txt
   - Best for Isadora projects that only need the local venv structure
     for Pythoner to detect and use automatically.
   - Configure inputs as:
       - *Venv Folder Name*: (blank or "Virtual_Env")
       - *Filepath for Venv Creation*: (blank)
       - *Use Requirements*: 0 (False)
       - *Trigger*: 1 (True)

2. **Custom path mode (advanced / Version 2)**
   - Creates a venv in a user-specified path and optionally installs
     packages from requirements.txt located in that same folder.
   - Suitable for shared or multi-project setups that need a pip-managed
     environment.
   - Configure inputs as:
       - *Venv Folder Name*: name of venv folder (e.g. "env")
       - *Filepath for Venv Creation*: absolute path to parent directory
       - *Use Requirements*: 1 (True)
       - *Trigger*: 1 (True)

PLATFORM NOTES
===============
- **Windows**:
    - Uses the embedded Python from the Pythoner plugin.
    - Creates a missing `DLLs/` folder beside Pythoner if required.
    - Adds a `.pth` file inside the venv so `encodings` and stdlib can load.
    - Subprocesses are launched with `CREATE_NO_WINDOW` for silent operation.

- **macOS**:
    - Uses symlinks (`--symlinks`) instead of copies to preserve framework
      loader paths, preventing `dyld` errors.
    - Adds `DYLD_FRAMEWORK_PATH` during health checks and pip installs.
    - Protects against writing inside the signed `.izzyplug` bundle to
      preserve code signing integrity.

This script unifies both workflows while maintaining compatibility and
reliability on both platforms.
"""


def get_default_pythoner_path():
    if platform.system() == "Windows":
        return r"C:\Program Files\Common Files\TroikaTronix\Isadora Plugins\Pythoner.izzyplug\python.exe"
    elif platform.system() == "Darwin":
        base = ("/Library/Application Support/TroikaTronix/IsadoraPlugins_x64/"
                "Pythoner.izzyplug/Contents/Frameworks/Python.framework/Versions")
        cand1 = os.path.join(base, "Current", "bin", "python")
        cand2 = os.path.join(base, "Current", "bin", "python3")
        if os.path.exists(cand1): return cand1
        if os.path.exists(cand2): return cand2
        try:
            versions = sorted([d for d in os.listdir(base) if d[:1].isdigit()])
            for v in reversed(versions):
                p1 = os.path.join(base, v, "bin", "python")
                p2 = os.path.join(base, v, "bin", "python3")
                if os.path.exists(p1): return p1
                if os.path.exists(p2): return p2
        except Exception:
            pass
        return None
    else:
        return None


# ---------- utilities ----------

def run_command_with_progress(cmd_list, working_dir=None, env=None):
    creationflags = 0
    if platform.system() == "Windows":
        creationflags = subprocess.CREATE_NO_WINDOW
    process = subprocess.Popen(
        cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=working_dir,
        env=env,
        text=True,
        bufsize=1,
        creationflags=creationflags
    )
    output = ""
    for line in process.stdout:
        print(line.rstrip())
        output += line
    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd_list, output)
    return output


def ensure_windows_dlls_folder(pythoner_path):
    if platform.system() == "Windows":
        base_dir = os.path.dirname(pythoner_path)
        dlls_path = os.path.join(base_dir, "DLLs")
        if not os.path.exists(dlls_path):
            try:
                os.makedirs(dlls_path)
                print(f"[Info] Created missing DLLs folder at: {dlls_path}")
            except Exception as e:
                print(f"[Warning] Could not create DLLs folder: {e}")


def _venv_python_path(venv_path):
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        cand = os.path.join(venv_path, "bin", "python3")
        return cand if os.path.exists(cand) else os.path.join(venv_path, "bin", "python")


def _ensure_stdlib_for_embedded_windows(pythoner_path, venv_path):
    if platform.system() != "Windows":
        return None
    base = os.path.dirname(pythoner_path)
    scripts = os.path.join(venv_path, "Scripts")
    if not os.path.isdir(scripts):
        return "Warning: venv Scripts folder not found."
    candidates = [p for p in os.listdir(base)
                  if p.startswith("python3") and os.path.isdir(os.path.join(base, p))]
    if not candidates:
        return "Warning: No stdlib folder (python3XY) found beside embedded Python."
    stdlib_dirname = sorted(candidates)[-1]
    stdlib_dir = os.path.join(base, stdlib_dirname)
    ver_suffix = stdlib_dirname.replace("python", "")
    pth_path = os.path.join(scripts, f"python{ver_suffix}._pth")
    try:
        with open(pth_path, "w", encoding="utf-8") as f:
            f.write(stdlib_dir + "\n.\nimport site\n")
        print(f"[Info] Wrote {os.path.basename(pth_path)} pointing to {stdlib_dir}")
        return None
    except Exception as e:
        return f"Warning: Could not write {os.path.basename(pth_path)}: {e}"


def _health_check_python(py_exe, env=None):
    try:
        out = run_command_with_progress([py_exe, "-c", "import encodings, sys; print('OK', sys.version)"],
                                        env=env)
        return True, out.strip()
    except subprocess.CalledProcessError as e:
        return False, (e.output if hasattr(e, "output") else str(e))


# ---------- macOS helpers ----------

def _find_macos_bundle_root(path):
    if platform.system() != "Darwin":
        return None
    cur = os.path.abspath(path)
    while True:
        head, tail = os.path.split(cur)
        if not tail:
            return None
        if tail.endswith(".izzyplug"):
            return cur
        cur = head


def _is_under(child, parent):
    child = os.path.abspath(child)
    parent = os.path.abspath(parent)
    try:
        return os.path.commonpath([child, parent]) == parent
    except Exception:
        return False


def _darwin_framework_root(pythoner_path):
    if platform.system() != "Darwin":
        return None
    parts = os.path.abspath(pythoner_path).split("/")
    if "Python.framework" in parts:
        idx = parts.index("Python.framework")
        return "/".join(parts[:idx+1])
    return None


# ---------- main ----------

def python_main(venv_folder_name, venv_creation_path, use_requirements, izzyTrigger):
    if not izzyTrigger:
        return

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    venv_folder_name = (venv_folder_name or "").strip() or "Virtual_Env"
    venv_creation_path = (venv_creation_path or "").strip() or project_root

    if not re.match(r"^[a-zA-Z0-9_\-]+$", venv_folder_name):
        msg = "Error: Invalid characters in the virtual environment folder name."
        print(msg); return msg

    if not os.path.isabs(venv_creation_path):
        msg = "Error: The provided path is not an absolute path."
        print(msg); return msg
    try:
        os.makedirs(venv_creation_path, exist_ok=True)
    except Exception as e:
        msg = f"Error: Could not create parent directory:\n{venv_creation_path}\n{e}"
        print(msg); return msg

    full_venv_path = os.path.join(venv_creation_path, venv_folder_name)

    venv_indicators = ['Lib', 'Scripts', 'bin', 'pyvenv.cfg']
    if any(os.path.exists(os.path.join(full_venv_path, it)) for it in venv_indicators):
        msg = f"Error: The directory '{full_venv_path}' already contains a virtual environment."
        print(msg); return msg

    pythoner_path = get_default_pythoner_path()
    if not pythoner_path or not os.path.exists(pythoner_path):
        msg = "Error: Could not determine the Pythoner interpreter path."
        print(msg); return msg

    if platform.system() == "Darwin":
        bundle_root = _find_macos_bundle_root(pythoner_path)
        if bundle_root and _is_under(full_venv_path, bundle_root):
            msg = ("Refusing to write inside the Pythoner bundle on macOS "
                   "(would break code signing). Choose another venv location.")
            print(msg); return msg

    clean_env = os.environ.copy()
    clean_env.pop("PYTHONHOME", None)
    clean_env.pop("PYTHONPATH", None)

    mac_env = clean_env.copy()
    if platform.system() == "Darwin":
        fw_root = _darwin_framework_root(pythoner_path)
        if fw_root and os.path.isdir(fw_root):
            mac_env["DYLD_FRAMEWORK_PATH"] = fw_root

    ensure_windows_dlls_folder(pythoner_path)

    try:
        print("[Stage 1] Creating virtual environment…")
        create_args = ["--no-download", "--python", pythoner_path]
        if platform.system() == "Darwin":
            create_args.insert(0, "--symlinks")
        else:
            create_args.insert(0, "--copies")

        run_command_with_progress(
            [pythoner_path, "-m", "virtualenv", *create_args, full_venv_path],
            working_dir=venv_creation_path,
            env=clean_env
        )

        python_path = _venv_python_path(full_venv_path)
        print(f"[Debug] Using Python at: {python_path}")
        if not os.path.exists(python_path):
            msg = f"Error: Could not find Python in virtual environment at: {python_path}"
            print(msg); return msg

        warn = _ensure_stdlib_for_embedded_windows(pythoner_path, full_venv_path)
        if warn:
            print(warn)

        print("[Health] Checking stdlib import (encodings)…")
        env_for_venv = mac_env if platform.system() == "Darwin" else clean_env
        ok, health_msg = _health_check_python(python_path, env=env_for_venv)
        if not ok:
            msg = f"Venv created but failed stdlib health check:\n{health_msg}"
            print(msg); return msg
        else:
            print(f"[Health] {health_msg}")

        if not bool(use_requirements):
            msg = f"Virtual environment created successfully at {full_venv_path}"
            print("[Stage 2] Skipping pip/requirements as requested.")
            print(msg); return msg

        print("[Stage 2] Upgrading pip…")
        run_command_with_progress(
            [python_path, "-m", "pip", "install", "--upgrade", "pip"],
            working_dir=venv_creation_path,
            env=env_for_venv
        )

        requirements_path = os.path.join(venv_creation_path, "requirements.txt")
        if not os.path.exists(requirements_path):
            msg = "Error: requirements.txt not found in the provided path."
            print(msg); return msg

        print("[Stage 3] Installing packages from requirements.txt…")
        run_command_with_progress(
            [python_path, "-m", "pip", "install", "-r", requirements_path],
            working_dir=venv_creation_path,
            env=env_for_venv
        )

        print("[Stage 4] Done.")
        msg = f"Virtual environment created successfully at {full_venv_path}"
        print(msg); return msg

    except subprocess.CalledProcessError as e:
        msg = f"Error during setup: {e}"
        print(msg)
        return msg
