#!/usr/bin/env python3

import argparse
import os
import pathlib
import subprocess
import sys
import tomllib

REGISTRY_PREFIX = "registry+"


def fail(message):
    print(f"cargo-inject-patches: error: {message}", file=sys.stderr)
    sys.exit(1)


def compat_class(version):
    """Cargo's caret-compatibility class: versions sharing one are interchangeable."""
    core = version.split("+")[0].split("-")[0]
    parts = [int(x) for x in core.split(".")] + [0, 0]
    major, minor, patch = parts[0], parts[1], parts[2]
    if major:
        return (major,)
    if minor:
        return (0, minor)
    return (0, 0, patch)


def load_patch_table():
    """Map crate name -> compatibility class -> the port that supersedes it."""
    cargo_home = os.environ.get("CARGO_HOME")
    if not cargo_home:
        fail("CARGO_HOME is not set, cannot locate the [patch.crates-io] table")

    config = os.path.join(cargo_home, "config.toml")
    if not os.path.exists(config):
        fail(f"{config} does not exist")

    with open(config, "rb") as f:
        patches = tomllib.load(f).get("patch", {}).get("crates-io", {})

    table = {}
    for key, spec in patches.items():
        # The key is only a rename; "package" carries the real crate name.
        name = spec.get("package", key)
        port = os.path.join(spec["path"], "Cargo.toml")
        if not os.path.exists(port):
            fail(f"patch `{key}` points at {spec['path']}, which has no Cargo.toml")

        with open(port, "rb") as f:
            version = tomllib.load(f).get("package", {}).get("version")
        if not isinstance(version, str):
            fail(f"patch `{key}` has a non-literal version, which we cannot resolve")

        table.setdefault(name, {})[compat_class(version)] = (version, spec["path"])
    return table


def load_lock(lockfile):
    with open(lockfile, "rb") as f:
        return tomllib.load(f).get("package", [])


def unpatched(lockfile, table):
    """Lock entries still coming from the registry that a patched port supersedes."""
    pending = []
    for pkg in load_lock(lockfile):
        source = pkg.get("source", "")
        if not source.startswith(REGISTRY_PREFIX):
            continue
        port = table.get(pkg["name"], {}).get(compat_class(pkg["version"]))
        if port:
            pending.append((pkg["name"], pkg["version"], port))
    return pending


parser = argparse.ArgumentParser(description="Inject patched Rust libraries into Cargo lockfiles")
parser.add_argument("manifest", type=pathlib.Path, help="path to Cargo.toml")
manifest = parser.parse_args().manifest

table = load_patch_table()

# The lockfile lives next to the workspace root, which need not be the given manifest.
root = subprocess.run(
    ["cargo", "locate-project", "--workspace", "--message-format", "plain",
     "--manifest-path", manifest],
    capture_output=True,
)
if root.returncode:
    fail(f"cargo locate-project failed:\n{root.stderr.decode('utf-8')}")
lockfile = os.path.join(os.path.dirname(root.stdout.decode("utf-8").strip()), "Cargo.lock")

if not os.path.exists(lockfile):
    # Resolving from scratch already applies the patches, so this needs no update pass.
    print("cargo-inject-patches: no lockfile, generating one...")
    generate = subprocess.run(
        ["cargo", "generate-lockfile", "--manifest-path", manifest], capture_output=True
    )
    if generate.returncode:
        fail(f"cargo generate-lockfile failed:\n{generate.stderr.decode('utf-8')}")

pending = unpatched(lockfile, table)

if not pending:
    print("cargo-inject-patches: patches already applied, nothing to do")
    sys.exit(0)

# Only ever update the patched crates by exact version: a bare `cargo update` would
# re-resolve the whole graph and drift every unrelated dependency off its pin.
cmd = ["cargo", "update", "--manifest-path", manifest]
cmd += [f"-p{name}@{version}" for name, version, _ in pending]

output = subprocess.run(cmd, capture_output=True)
if output.returncode:
    fail(f"cargo update failed:\n{output.stderr.decode('utf-8')}")

# Cargo only warns when a patch does not apply and carries on with the unpatched crate,
# so re-reading the lockfile is the one reliable way to tell that it took effect.
stuck = unpatched(lockfile, table)
if stuck:
    fail("the following crates could not be patched, most likely because the port is "
         "older than what the dependency graph requires:\n"
         + "\n".join(f"  {name} {version} is not superseded by {port[0]} in {port[1]}"
                     for name, version, port in stuck))
