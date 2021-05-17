#!/usr/bin/env python3

import argparse, os, subprocess, pathlib

patched_libs = {
	'libc': '0.2.93',
	'num_cpus': '1.13.0',
	'users': '0.11.0',
}

parser = argparse.ArgumentParser(description='Inject patched Rust libraries into Cargo lockfiles')
parser.add_argument('manifest', type=pathlib.Path, help='path to Cargo.toml')
manifest = parser.parse_args().manifest

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
