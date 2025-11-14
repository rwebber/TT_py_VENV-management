import os
import re
import sys
import json
import ssl
import urllib.request
import urllib.error
import platform

# iz_input 1 "project_path"
# iz_input 2 "trigger"
# iz_output 1 "status"

# Use system default SSL context
_default_ctx = ssl.create_default_context()

# ----------------------------
# Helpers: environment tagging
# ----------------------------

def _py_tags():
    """
    Return a set of acceptable python and abi tags for this interpreter.
    Examples (CPython 3.11): {'cp311', 'py311', 'py31', 'py3'}
    Accept ABI: {'cp311', 'abi3', 'none'}  (the 'none' is for pure-python)
    """
    impl = platform.python_implementation()
    major, minor = sys.version_info[:2]

    tags = set()
    abi = set()

    # Python tags commonly seen in wheels
    # e.g., cp311, cp310; py311; py3; py2.py3 (in filename it’ll be 'py2.py3')
    if impl == "CPython":
        tags.add(f"cp{major}{minor}")
        abi.add(f"cp{major}{minor}")  # exact ABI for CPython
        abi.add("abi3")               # stable ABI wheels are often OK
    # Generic python tags accepted for any implementation of given version
    tags.add(f"py{major}{minor}")
    # include broader py3 tag (many wheels publish 'py3')
    tags.add(f"py{major}")

    # Pure-python ABI tag:
    abi.add("none")

    return tags, abi

def _platform_tags():
    """
    Return a set of acceptable *platform* tags for this machine.
    Includes 'any' for pure-python wheels.
    """
    plat = sys.platform
    machine = platform.machine().lower()
    tags = set(["any"])  # pure-python wheel platform tag

    # Normalize arch
    arch = None
    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    elif machine in ("i386", "i686", "x86"):
        arch = "i386"
    elif machine.startswith("armv7"):
        arch = "armv7l"

    if plat.startswith("win"):
        # Common Windows platform tags
        if arch == "x86_64":
            tags.add("win_amd64")
        elif arch == "arm64":
            tags.add("win_arm64")
        elif arch in ("i386",):
            tags.add("win32")

    elif plat == "darwin":
        # macOS tags look like: macosx_10_9_x86_64, macosx_11_0_arm64, macosx_11_0_universal2
        # We’ll generate a small ladder of versions from current down a few releases.
        mac_ver_str, _, _ = platform.mac_ver()
        if mac_ver_str:
            parts = mac_ver_str.split(".")
            try:
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
            except Exception:
                major, minor = 11, 0  # assume modern macOS if parsing fails
        else:
            major, minor = 11, 0

        # Produce a few downward-compatible tags (wheels often ship with minimums like 10_9)
        ladder = []
        if major >= 11:
            # macOS 11+ uses major as the first number
            for mj in range(major, max(10, major - 5), -1):
                ladder.append((mj, 0))
        else:
            # pre-11 style (10.x)
            for mn in range(minor, max(0, minor - 5), -1):
                ladder.append((10, mn))

        arch_opts = set()
        if arch == "x86_64":
            arch_opts.update(["x86_64", "universal2"])  # universal2 often works
        elif arch == "arm64":
            arch_opts.update(["arm64", "universal2"])
        else:
            # fallback: accept both common mac arches
            arch_opts.update(["x86_64", "arm64", "universal2"])

        for (mj, mn) in ladder:
            for a in arch_opts:
                tags.add(f"macosx_{mj}_{mn}_{a}")

    else:
        # Linux & others
        # Wheels commonly have manylinux*/musllinux*/linux_* tags.
        # We accept general linux tags for the matching arch.
        if arch in ("x86_64", "arm64", "i386", "armv7l"):
            tags.add(f"linux_{arch}")
            # manylinux / musllinux (broad acceptance for our purposes)
            tags.update({
                f"manylinux1_{arch}", f"manylinux2010_{arch}", f"manylinux2014_{arch}",
                f"manylinux_2_17_{arch}", f"manylinux_2_28_{arch}",
                f"musllinux_1_1_{arch}"
            })

    return tags

_PY_TAGS, _ABI_TAGS = _py_tags()
_PLAT_TAGS = _platform_tags()

# ----------------------------
# Helpers: wheel parsing/check
# ----------------------------

_WHEEL_RX = re.compile(
    r"""^(?P<namever>.+?)-
        (?P<pyver>[A-Za-z0-9\.]+)-
        (?P<abi>[A-Za-z0-9\.]+)-
        (?P<plat>[A-Za-z0-9\._]+)
        \.whl$""",
    re.VERBOSE
)

def _wheel_tags_from_filename(filename):
    """
    Parse a wheel filename and return (py_tags, abi_tags, plat_tags) as sets.
    Supports multiple dot-separated tags in each field.
    """
    m = _WHEEL_RX.match(filename)
    if not m:
        return set(), set(), set()

    py = set(m.group("pyver").split("."))
    abi = set(m.group("abi").split("."))
    plat = set(m.group("plat").split("."))
    return py, abi, plat

def _is_wheel_compatible(filename):
    """
    Compatibility heuristic:
    - If platform contains 'any' and abi contains 'none' -> pure python; require python tag match.
    - Otherwise require:
        * python tag matches one of our _PY_TAGS
        * abi is one of our _ABI_TAGS (or contains 'none' when pure)
        * platform tag matches one of our _PLAT_TAGS
      We accept compatibility if ANY combination in dot-sets intersect suitably.
    """
    py_tags, abi_tags, plat_tags = _wheel_tags_from_filename(filename)
    if not py_tags and not abi_tags and not plat_tags:
        return False

    # Python tag match
    if not (py_tags & _PY_TAGS):
        # Handle py2.py3 style combo: if it contains 'py3' and we're py3, accept.
        if f"py{sys.version_info[0]}" not in py_tags:
            return False

    # Platform/ABI handling
    # Pure-python case:
    if ("any" in plat_tags) and ("none" in abi_tags):
        return True

    # ABI match (cpXY or abi3)
    if not (abi_tags & _ABI_TAGS):
        return False

    # Platform match
    if not (plat_tags & _PLAT_TAGS):
        return False

    return True

# --------------------------------------
# Pythoner lifecycle wrappers (unchanged)
# --------------------------------------

def python_init(project_path, trigger):
    return

def python_main(project_path, trigger):
    """
    Validates versions listed in requirements.txt using PyPI API.
    Checks if version exists AND if a compatible wheel is likely available.
    """
    if not trigger:
        return "❌"

    req_path = os.path.join(project_path, 'requirements.txt')
    if not os.path.isfile(req_path):
        return f"Error: requirements.txt not found at {req_path}"

    status_messages = []
    with open(req_path, 'r', encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
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
                with urllib.request.urlopen(url, context=_default_ctx) as resp:
                    data = json.load(resp)
            except urllib.error.URLError as e:
                # Attempt insecure fallback for problematic cert stores
                if isinstance(getattr(e, "reason", None), ssl.SSLError):
                    try:
                        insecure_ctx = ssl._create_unverified_context()
                        with urllib.request.urlopen(url, context=insecure_ctx) as resp:
                            data = json.load(resp)
                            ssl_warning = True
                    except Exception as fe:
                        status_messages.append(f"❌ SSL error checking {pkg}: {fe}")
                        continue
                else:
                    status_messages.append(f"❌ URLError checking {pkg}: {e}")
                    continue
            except Exception as e:
                status_messages.append(f"❌ Error checking {pkg}: {e}")
                continue

            if not data:
                status_messages.append(f"❌ No data returned for {pkg}")
                continue

            releases = data.get("releases", {})
            available_versions = list(releases.keys())

            if version in releases:
                files = releases.get(version, [])
                wheels = [f for f in files if f.get("filename", "").endswith(".whl")]

                compatible = False
                for wh in wheels:
                    fname = wh.get("filename", "")
                    if _is_wheel_compatible(fname):
                        compatible = True
                        break

                if compatible:
                    msg = f"✅ {pkg}=={version} is available and compatible"
                elif wheels:
                    msg = f"⚠️ {pkg}=={version} exists but has NO compatible wheel for this platform"
                else:
                    msg = f"⚠️ {pkg}=={version} exists but only as source (no wheels)"
            else:
                latest = sorted(available_versions)[-1] if available_versions else "N/A"
                msg = f"❌ {pkg}=={version} not found (latest: {latest})"

            if ssl_warning:
                msg += " (SSL fallback used)"

            status_messages.append(msg)

    return "\n".join(status_messages) if status_messages else "✅ All entries valid."

def python_finalize():
    pass

if __name__ == '__main__':
    test_path = r"/your/project/path"
    print(python_main(test_path, True))
    python_finalize()
