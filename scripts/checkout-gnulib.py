#!/usr/bin/env python3

import argparse
import pathlib
import subprocess
import sys

def main():
	parser = argparse.ArgumentParser(description="Helper for checking out gnulib")
	parser.add_argument("repo", type=pathlib.Path, help="path to the repo")
	parser.add_argument("path", type=pathlib.Path, default="gnulib", help="where to check out gnulib to", nargs='?')

	args = parser.parse_args()

	if not (args.path / '.git').exists():
		result = subprocess.run(["git", "clone", args.repo, args.path])
		sys.exit(result.returncode)
	sys.exit(0)

if __name__ == "__main__":
    main()
