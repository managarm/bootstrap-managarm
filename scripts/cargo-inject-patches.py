#!/usr/bin/env python3

import argparse, os, subprocess, pathlib

patched_libs = {
	'libc': '0.2.117',
	'num_cpus': '1.13.0',
	'users': '0.11.0',
    'backtrace': '0.3.64',
}

parser = argparse.ArgumentParser(description='Inject patched Rust libraries into Cargo lockfiles')
parser.add_argument('manifest', type=pathlib.Path, help='path to Cargo.toml')
manifest = parser.parse_args().manifest

# First, delete the existing lockfile to work around https://github.com/rust-lang/cargo/issues/9470
lockfile = os.path.join(os.path.dirname(manifest), 'Cargo.lock')
if os.path.exists(lockfile):
    print('cargo-inject-patches: workaround cargo bug by removing existing lockfile...')
    os.remove(lockfile)

for lib, version in patched_libs.items():
	cmd = [
		'cargo',
		'update',
		'--manifest-path', manifest,
		'--package', lib,
		'--precise', version
	]

	output = subprocess.run(cmd, capture_output=True)
	if 'did not match any packages' in str(output.stderr):
		print(f'cargo-inject-patches: Injecting {lib} v{version} failed, patch not used')
	else:
		print(f'cargo-inject-patches: Injected {lib} v{version}')
