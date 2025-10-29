#!/usr/bin/env python3

import argparse
import os
import pathlib
import subprocess

patched_libs = {
    "backtrace": "0.3.75",
    "calloop": "0.10.0",
    'getrandom': ['0.2.15', '0.3.2'],
    "libc": "0.2.175",
    "libloading": ['0.7.4', '0.8.6'],
    "mio": ["0.6.23", "0.8.3", "1.0.3"],
    "nix": ["0.24.3", "0.29.0"],
    "num_cpus": "1.15.0",
    "users": "0.11.0",
    "winit": "0.27.5",
    "glutin": "0.29.1",
    "glutin_glx_sys": "0.1.7",
    "glutin_egl_sys": "0.1.5",
    "shared_library": "0.1.9",
    "errno": "0.3.10",
    "rustix": ["0.38.44", "1.0.5"],
    "uzers": "0.12.1",
    "cc": "1.2.17",
    "termios": "0.3.3",
    "mac_address": "1.2.8",
    "lua-src": "547.0.0",
    "starship-battery": "0.10.1",
    "socket2": "0.5.9",
    "libssh-rs-sys": "0.2.6",
    "wayland-backend": "0.3.8",
    "wayland-sys": "0.3.8",
    "ring": "0.17.14",
    "zbus": "4.4.0",
    "zvariant": "4.4.0",
    "target-lexicon": "0.13.3",
    "cfg-expr": "0.20.3"
}

parser = argparse.ArgumentParser(description="Inject patched Rust libraries into Cargo lockfiles")
parser.add_argument("manifest", type=pathlib.Path, help="path to Cargo.toml")
manifest = parser.parse_args().manifest

# First, delete the existing lockfile to work around https://github.com/rust-lang/cargo/issues/9470
lockfile = os.path.join(os.path.dirname(manifest), "Cargo.lock")
if os.path.exists(lockfile):
    print("cargo-inject-patches: workaround cargo bug by removing existing lockfile...")
    os.remove(lockfile)

cmd = ["cargo", "update", "--manifest-path", manifest]

for name, versions in patched_libs.items():
    if isinstance(versions, str):
        cmd.append(f"-p{name}@{versions}")
    else:
        for v in versions:
            cmd.append(f"-p{name}@{v}")

output = subprocess.run(cmd, capture_output=True)
for line in output.stderr.decode('utf-8').splitlines():
    if line.startswith("Patch `"):
        print(line)
