#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess
from pathlib import Path

KEYS_DIR = Path(__file__).parent / "../extrafiles/xbps-keys"


def do_sysroot(args):
    root = Path("system-root")

    # Install signing keys.
    key_dir = root / "var/db/xbps/keys"
    key_dir.mkdir(parents=True, exist_ok=True)
    for key_file in KEYS_DIR.iterdir():
        shutil.copy(key_file, key_dir / key_file.name)

    # Run xbps-install.
    xbps_install = Path.home() / ".xbstrap/bin/xbps-install"
    env = {**os.environ, "XBPS_TARGET_ARCH": args.arch}

    subprocess.run(
        [xbps_install, "-y", "-i", "-R", args.repo_url, "-S", "-r", root, "base", "limine"],
        env=env,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--arch", default="x86_64", help="Target architecture for XBPS_TARGET_ARCH"
    )
    parser.add_argument(
        "--repo-url",
        default="https://repos.managarm.org/repos/amd64/",
        help="xbps package repository URL",
    )
    subparsers = parser.add_subparsers(required=True)

    sysroot_parser = subparsers.add_parser("sysroot")
    sysroot_parser.set_defaults(func=do_sysroot)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
