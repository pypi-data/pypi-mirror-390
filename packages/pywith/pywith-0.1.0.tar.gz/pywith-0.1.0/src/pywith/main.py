import argparse
import os
import pathlib
import shutil
import sys


def main():
    args = parse_args()
    packages = ",".join(args.package)

    # Prefer uvx from the venv bin directory
    venv_bin = pathlib.Path(sys.prefix) / "bin" / "uvx"
    uvx = str(venv_bin) if venv_bin.exists() else shutil.which("uvx")

    cmd = [uvx, "--with", packages, "ptpython"]
    os.execv(cmd[0], cmd)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch ptpython with custom packages.",
    )
    parser.add_argument(
        "package",
        type=str,
        nargs="+",
        help="Name of package to include in the ptpython environment.",
    )
    return parser.parse_args()
