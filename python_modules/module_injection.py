"""
In-memory module injector utilizing gz64-encoded JSON maps.

This method allows User Actors in Isadora to include some Pute Python modules without the need for a virtual
environment or downloading.

This module defines functionality to dynamically add Python modules and
packages to the environment based on gz64-encoded JSON maps. Such modules
are temporarily stored in-memory and served through a custom importer.
The injection is aimed to blend seamlessly with existing Python imports
and provides conveniences like optional testing of the environment post-injection.
"""

# iz_input 1 "GZ64 Map"     - base64(gzip(JSON mapping: {"packaging/__init__.py": "...", ...}))
#                              Or the literal string "__SELFTEST__" to run a built-in self test.
# iz_input 2 "Extra GZ64"   - (optional) JSON list of additional gz64 maps: ["...","..."]
# iz_output 1 "Status / Log"

import sys, json, gzip, base64, importlib.abc, importlib.util

# ---------------- In-memory module store + importer ----------------

_INJECTED_FILES = {}    # path -> source text
_DICT_FINDER = None
_LAST_STATUS = ""

def _set_status(msg: str) -> str:
    global _LAST_STATUS
    _LAST_STATUS = str(msg)
    return _LAST_STATUS

class DictFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Serve pure-Python modules from an in-memory {path->source} mapping."""
    def __init__(self, files_map): self.files = files_map

    def find_spec(self, fullname, path, target=None):
        mod_path = fullname.replace(".", "/")
        file_key = f"{mod_path}.py"
        pkg_init_key = f"{mod_path}/__init__.py"
        if file_key in self.files:
            return importlib.util.spec_from_loader(fullname, self, origin=file_key, is_package=False)
        if pkg_init_key in self.files:
            return importlib.util.spec_from_loader(fullname, self, origin=pkg_init_key, is_package=True)
        return None

    def create_module(self, spec): return None  # default module

    def exec_module(self, module):
        fullname = module.__spec__.name
        mod_path = fullname.replace(".", "/")
        file_key = f"{mod_path}.py"
        pkg_init_key = f"{mod_path}/__init__.py"

        code_text = self.files.get(file_key)
        is_pkg = False
        if code_text is None:
            code_text = self.files.get(pkg_init_key)
            if code_text is None:
                raise ImportError(f"Module source not found for {fullname}")
            is_pkg = True

        module.__file__ = module.__spec__.origin
        if is_pkg:
            module.__package__ = fullname
            module.__path__ = [fullname]  # placeholder so submodule imports work
        else:
            module.__package__ = fullname.rpartition('.')[0]

        exec(compile(code_text, module.__file__, "exec"), module.__dict__)

# ---------------- Helpers ----------------

def _ensure_finder():
    global _DICT_FINDER
    if _DICT_FINDER is None:
        _DICT_FINDER = DictFinder(_INJECTED_FILES)
        sys.meta_path.insert(0, _DICT_FINDER)

def _load_gz64_map(gz64_text: str) -> dict:
    if not gz64_text: return {}
    data = gzip.decompress(base64.b64decode(gz64_text))
    return json.loads(data.decode("utf-8"))

def _top_pkg(path: str) -> str:
    # "packaging/version.py" -> "packaging"
    return path.split("/", 1)[0] if "/" in path else path.split(".py", 1)[0]

def _partition_by_pkg(files_map: dict) -> dict:
    # {"packaging/..": "...", "pythonosc/..": "..."} -> {"packaging": {...}, "pythonosc": {...}}
    buckets = {}
    for k, v in files_map.items():
        pkg = _top_pkg(k)
        buckets.setdefault(pkg, {})[k] = v
    return buckets

def _is_importable(pkg: str) -> bool:
    try:
        return importlib.util.find_spec(pkg) is not None
    except Exception:
        return False

# def _set_status(msg: str) -> str:
#     global _LAST_STATUS
#     _LAST_STATUS = str(msg)
#     try:
#         iz_output[1] = _LAST_STATUS  # provided by Pythoner at runtime
#     except Exception:
#         # When running in an IDE, iz_output is undefined; ignore
#         pass
#     return _LAST_STATUS

def _selftest_map() -> dict:
    # Tiny fake package that won't exist in env
    return {
        "mypkg/__init__.py": "from .version import VERSION\n",
        "mypkg/version.py": "VERSION='0.1.0'\n",
    }

# def run_injection(gz64_map: str, extra_gz64_json: str, test_snip: str) -> str:
#     """
#     Prefer user's environment; inject only if missing.
#     Accepts one primary gz64 map and optional JSON list of extra gz64 maps.
#     Optionally runs `test_snip` where setting `status = "..."`
#     customizes the returned status string.
#     """
#     # 1) Collect candidate maps
#     candidate_maps = []
#     if isinstance(gz64_map, str) and gz64_map.strip():
#         if gz64_map.strip() == "__SELFTEST__":
#             candidate_maps.append(_selftest_map())
#         else:
#             candidate_maps.append(_load_gz64_map(gz64_map.strip()))
#
#     if isinstance(extra_gz64_json, str) and extra_gz64_json.strip():
#         try:
#             arr = json.loads(extra_gz64_json)
#             if not isinstance(arr, list):
#                 return "Extra GZ64 must be a JSON list of strings."
#             for gz in arr:
#                 if isinstance(gz, str) and gz.strip():
#                     candidate_maps.append(_load_gz64_map(gz.strip()))
#         except Exception as e:
#             return f"Extra maps JSON error: {e}"
#
#     if not candidate_maps:
#         return "No maps provided."
#
#     # 2) For each top-level package, inject only if not importable
#     injected_pkgs, found_pkgs = [], []
#     for files_map in candidate_maps:
#         by_pkg = _partition_by_pkg(files_map)
#         for pkg, pkg_map in by_pkg.items():
#             if _is_importable(pkg):
#                 found_pkgs.append(pkg)
#                 continue
#             _INJECTED_FILES.update(pkg_map)
#             injected_pkgs.append(pkg)
#
#     if not injected_pkgs and not found_pkgs:
#         return "No recognizable packages in provided maps."
#
#     # Install finder only if we injected something
#     if injected_pkgs:
#         _ensure_finder()
#         import importlib
#         importlib.invalidate_caches()
#
#     # 3) Optional test snippet
#     if isinstance(test_snip, str) and test_snip.strip():
#         loc = {"status": None}
#         exec(test_snip, {}, loc)
#         if loc.get("status") is not None:
#             return str(loc["status"])
#
#     # 4) Compose clear status with detailed injection info
#     parts = []
#     if found_pkgs:
#         parts.append("FOUND: " + ", ".join(sorted(set(found_pkgs))))
#
#     if injected_pkgs:
#         # Summarize files per injected package
#         per_pkg_counts = {}
#         for path in _INJECTED_FILES.keys():
#             top = _top_pkg(path)
#             if top in injected_pkgs:
#                 per_pkg_counts[top] = per_pkg_counts.get(top, 0) + 1
#
#         # Build a short sample of injected file keys (limited for readability)
#         sample_keys = []
#         for k in _INJECTED_FILES.keys():
#             if _top_pkg(k) in injected_pkgs:
#                 sample_keys.append(k)
#             if len(sample_keys) >= 5:
#                 break
#
#         injected_list = ", ".join(sorted(set(injected_pkgs)))
#         counts_list = ", ".join(f"{pkg}:{cnt}" for pkg, cnt in sorted(per_pkg_counts.items()))
#         detail = f"INJECTED: {injected_list} (files={len(_INJECTED_FILES)}; per-pkg: {counts_list}"
#         if sample_keys:
#             detail += f"; sample: {', '.join(sample_keys)}"
#         detail += ")"
#         parts.append(detail)
#
#     return " | ".join(parts)


def run_injection(gz64_map: str, extra_gz64_json: str, test_snip: str) -> str:
    """
    Prefer user's environment; inject only if missing.
    Accepts one primary gz64 map and optional JSON list of extra gz64 maps.
    """
    # 1) Collect candidate maps
    candidate_maps = []
    if isinstance(gz64_map, str) and gz64_map.strip():
        if gz64_map.strip() == "__SELFTEST__":
            candidate_maps.append(_selftest_map())
        else:
            candidate_maps.append(_load_gz64_map(gz64_map.strip()))

    if isinstance(extra_gz64_json, str) and extra_gz64_json.strip():
        try:
            arr = json.loads(extra_gz64_json)
            if not isinstance(arr, list):
                return "Extra GZ64 must be a JSON list of strings."
            for gz in arr:
                if isinstance(gz, str) and gz.strip():
                    candidate_maps.append(_load_gz64_map(gz.strip()))
        except Exception as e:
            return f"Extra maps JSON error: {e}"

    if not candidate_maps:
        return "No maps provided."

    # 2) For each top-level package, inject only if not importable
    injected_pkgs, found_pkgs = [], []
    for files_map in candidate_maps:
        by_pkg = _partition_by_pkg(files_map)
        for pkg, pkg_map in by_pkg.items():
            if _is_importable(pkg):
                found_pkgs.append(pkg)
                continue
            _INJECTED_FILES.update(pkg_map)
            injected_pkgs.append(pkg)

    if not injected_pkgs and not found_pkgs:
        return "No recognizable packages in provided maps."

    # Install finder only if we injected something
    if injected_pkgs:
        _ensure_finder()
        import importlib
        importlib.invalidate_caches()

    # 3) Optional test snippet
    if isinstance(test_snip, str) and test_snip.strip():
        loc = {"status": None}
        exec(test_snip, {}, loc)
        if loc.get("status") is not None:
            return str(loc["status"])

    # 4) Compose clear status with detailed injection info
    parts = []
    if found_pkgs:
        parts.append("FOUND: " + ", ".join(sorted(set(found_pkgs))))

    if injected_pkgs:
        # Summarize files per injected package
        per_pkg_counts = {}
        for path in _INJECTED_FILES.keys():
            top = _top_pkg(path)
            if top in injected_pkgs:
                per_pkg_counts[top] = per_pkg_counts.get(top, 0) + 1

        # Build a short sample of injected file keys (limited for readability)
        sample_keys = []
        for k in _INJECTED_FILES.keys():
            if _top_pkg(k) in injected_pkgs:
                sample_keys.append(k)
            if len(sample_keys) >= 5:
                break

        injected_list = ", ".join(sorted(set(injected_pkgs)))
        counts_list = ", ".join(f"{pkg}:{cnt}" for pkg, cnt in sorted(per_pkg_counts.items()))
        detail = f"INJECTED: {injected_list} (files={len(_INJECTED_FILES)}; per-pkg: {counts_list}"
        if sample_keys:
            detail += f"; sample: {', '.join(sample_keys)}"
        detail += ")"
        parts.append(detail)

    return " | ".join(parts)



def _validate_injected_packages() -> str:
    """
    Attempt to import each top-level package we injected and report Pass/Fail.
    Returns a concise summary string.
    """
    import importlib
    # Determine which top-level packages were injected from the file keys
    injected_pkgs = sorted({ _top_pkg(p) for p in _INJECTED_FILES.keys() })
    if not injected_pkgs:
        return "Validate: no injected packages"

    results = []
    importlib.invalidate_caches()
    for pkg in injected_pkgs:
        try:
            importlib.import_module(pkg)
            results.append(f"{pkg}=Pass")
        except Exception as e:
            results.append(f"{pkg}=Fail({type(e).__name__})")
    return " | ".join(results)



def python_init(gz64_map, extra_gz64_json):
    try:
        summary = run_injection(gz64_map, extra_gz64_json, test_snip="")
        validate = _validate_injected_packages() if _INJECTED_FILES else "Validate: no injected packages"
        combined = summary if not summary else f"{summary} || {validate}"
        # If you have 1 output, return a string.
        # If you have N outputs, return a list/tuple of length N.
        print(combined)
        return _set_status(combined)
    except Exception as e:
        return _set_status(f"Injection error: {e}")

def python_main(*_unused):
    return _LAST_STATUS

def python_finalize():
    """
    Finalizes and cleans up global injections and dependencies added during runtime.
    """
    global _DICT_FINDER, _INJECTED_FILES  # ensure we refer to module-level vars

    if not _INJECTED_FILES:
        return  # nothing to clean up

    _set_status("")

    try:
        # 1. Remove all injected modules from sys.modules
        top_packages = {_top_pkg(path) for path in _INJECTED_FILES.keys()}
        for mod_name in list(sys.modules):
            if any(mod_name == pkg or mod_name.startswith(pkg + ".") for pkg in top_packages):
                del sys.modules[mod_name]

        # 2. Remove our DictFinder from sys.meta_path if present
        if _DICT_FINDER in sys.meta_path:
            sys.meta_path.remove(_DICT_FINDER)

        # 3. Clear globals
        _INJECTED_FILES.clear()
        _DICT_FINDER = None

        _set_status("Injection cleared")
    except Exception as e:
        _set_status(f"Cleanup error: {e}")

    print(_LAST_STATUS)


# ---------------- Standalone test harness (PyCharm) ----------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="In-memory module injector (gz64 JSON maps).")
    ap.add_argument("--map",   default="__SELFTEST__", help="Primary gz64 map string, or __SELFTEST__")
    ap.add_argument("--extra", default="",             help='JSON list of additional gz64 maps: ["...","..."]')
    ap.add_argument("--test",  default="",             help='Optional Python snippet; may set `status`')
    a = ap.parse_args()
    print(run_injection(a.map, a.extra, a.test))
