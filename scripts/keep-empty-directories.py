#! /usr/bin/env python3

import os
import sys

for path, dirs, files in os.walk(sys.argv[1]):
    if not dirs and not files:
        with open(os.path.join(path, ".keep"), "w"):
            pass
