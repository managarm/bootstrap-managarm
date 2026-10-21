#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROVISION = Path(__file__).parent / "../extrafiles/managarm-scripts/provision-sysroot.py"


def provision(root, *args):
    subprocess.run([sys.executable, PROVISION, "apply", "--root", root, *args], check=True)


def do_sysroot(args):
    root = Path("system-root")

    # xbps-install takes the repository and its signing key from the root, so this goes first.
    provision(root, "--arch", args.arch, f"--xbps-{args.xbps_channel}")
    # The host's xbps may have been built with another sysconfdir, so name the root's config explicitly.
    conf_dir = (root / "etc/xbps.d").resolve()

    # Run xbps-install.
    xbps_install = Path.home() / ".xbstrap/bin/xbps-install"
    env = {**os.environ, "XBPS_TARGET_ARCH": args.arch}

    subprocess.run(
        [xbps_install, "-y", "-S", "-r", root, "-C", conf_dir, "base", "limine"],
        env=env,
        check=True,
    )

    provision(
        root,
        "--user", "managarm",
        "--groups", "managarm", "wheel,users",
        "--password-hash", "managarm", "WJg36EZUlJ96k",
        "--password-hash", "root", "4T1CNB2BgzJeI",
        "--sshd-password-auth",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--arch", default="x86_64", help="Target architecture for XBPS_TARGET_ARCH"
    )
    xbps_group = parser.add_mutually_exclusive_group()
    xbps_group.add_argument(
        "--xbps-stable", dest="xbps_channel", action="store_const", const="stable",
        default="stable", help="Install from the stable xbps repository (default)",
    )
    xbps_group.add_argument(
        "--xbps-nightly", dest="xbps_channel", action="store_const", const="nightly",
        help="Install from the nightly xbps repository",
    )
    subparsers = parser.add_subparsers(required=True)

    sysroot_parser = subparsers.add_parser("sysroot")
    sysroot_parser.set_defaults(func=do_sysroot)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
