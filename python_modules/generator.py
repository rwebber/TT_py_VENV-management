# generator.py
"""
A script to bundle Python packages into compressed Base64 encoded data for distribution.

This script collects all Python (.py) files within a specified package's directory,
compresses them using gzip, encodes them in Base64, and outputs the result.
It is designed for creating portable representations of Python packages.

Functions:
    collect_pkg: Collects Python files from the specified package directory.
    gz64: Compresses data using gzip and encodes it in Base64.
"""
# Run this in the venv that has the package you want bundled:

#  run in terminal, in this files directory:
# python generator.py packaging > packaging_gz64.txt
# python generator.py pythonosc > pythonosc_gz64.txt
# python generator.py dx_system_helpers.py > dx_system_helpers_gz64.txt



import sys, json, os, sysconfig, gzip, base64, pathlib

def collect_pkg(target_path: str):
    path = pathlib.Path(target_path)

    if not path.exists():
        raise SystemExit(f"Target not found: {path}")

    files = {}

    # Handle single file
    if path.is_file() and path.suffix == ".py":
        key = path.name  # Just 'dx_system_helpers.py'
        files[key] = path.read_text(encoding="utf-8")
        return files

    # Handle package/folder
    if path.is_dir():
        for p in path.rglob("*.py"):
            rel = p.relative_to(path)
            key = f"{path.name}/{rel.as_posix()}"  # e.g. dx_system_helpers/__init__.py
            files[key] = p.read_text(encoding="utf-8")
        return files

    raise SystemExit(f"Unsupported file type: {path}")



def gz64(data: bytes) -> str:
    return base64.b64encode(gzip.compress(data, mtime=0)).decode("ascii")

if __name__ == "__main__":
    pkg = sys.argv[1]   # run like: python make_map_gz64.py packaging
    files_map = collect_pkg(pkg)
    blob = gz64(json.dumps(files_map).encode("utf-8"))
    print(blob)
