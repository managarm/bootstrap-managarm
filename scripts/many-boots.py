#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess
import uuid

def main():
    parser = argparse.ArgumentParser(description="Repeatedly boot and look for failures")
    parser.add_argument("--display", action="store_true",
                        help="Enable QEMU display (= do not pass -display none)")
    parser.add_argument("--halt", action="store_true",
                        help="Halt the VM on error (= do not use timeouts)")
    parser.add_argument("--wipe", action="store_true",
                        help="Remove log files from previous runs before starting")
    parser.add_argument("--timeout", type=int, default=60,
                        help="Timeout in seconds (default: 60)")
    parser.add_argument("--script", default="/usr/bin/true",
                        help="Script to run (default: /usr/bin/true)")
    args = parser.parse_args()

    if args.wipe:
        shutil.rmtree("many-boots", ignore_errors=True)

    os.makedirs("many-boots", exist_ok=True)
    os.makedirs("many-boots/good", exist_ok=True)
    os.makedirs("many-boots/bad", exist_ok=True)

    num_good = 0
    num_bad = 0
    while True:
        name = uuid.uuid4()

        env = os.environ.copy()
        if args.display:
            env["QFLAGS"] = "-snapshot"
        else:
            env["QFLAGS"] = "-snapshot -display none"

        scriptdir = os.path.dirname(os.path.realpath(__file__))
        vm_args = [
            os.path.join(scriptdir, "vm-util.py"),
            "qemu",
        ]
        if not args.halt:
            vm_args += [
                f"--timeout={args.timeout}",
                f"--io-timeout={args.timeout // 4}",
            ]
        vm_args += [
            f"--logfile=many-boots/{name}",
            f"--ci-script={args.script}",
        ]

        process = subprocess.Popen(
            vm_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            env=env,
        )
        try:
            process.communicate(timeout=2 * args.timeout)
        except subprocess.TimeoutExpired:
            print(f"Run {name} seems to be stuck")
            process.communicate()

        if process.returncode == 0:
            os.rename(f"many-boots/{name}", f"many-boots/good/{name}")
            num_good += 1
        else:
            os.rename(f"many-boots/{name}", f"many-boots/bad/{name}")
            num_bad += 1
        print(f"{num_good} good, {num_bad} bad")

if __name__ == "__main__":
    main()
