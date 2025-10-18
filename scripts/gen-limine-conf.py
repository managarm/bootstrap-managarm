#!/usr/bin/python3

import argparse
import contextlib


class Writer:
    __slots__ = (
        "base_cmdline",
        "out",
        "_level",
    )

    def __init__(self, out):
        self.out = out
        self._level = 0
        self.base_cmdline = ""

    def write_header(self):
        self.out.writelines(
            [
                "timeout: 3\n",
                # First entry is the default submenu.
                "default_entry: 2\n",
            ]
        )

    @contextlib.contextmanager
    def submenu(self, title):
        indent = " " * 4 * self._level
        slashes = "/" * (self._level + 1)
        self._level += 1
        self.out.writelines([f"{indent}{slashes}{title}\n"])
        yield
        self._level -= 1

    def write_entry(self, title, *, protocol, extra_cmdline=None):
        indent = " " * 4 * self._level
        slashes = "/" * (self._level + 1)
        subindent = " " * 4 * (self._level + 1)

        eir = {
            "limine": "eir-limine",
            "linux": "eir-linux.bin",
            "multiboot2": "eir-mb2",
            "efi": "eir-uefi",
        }[protocol]

        self.out.writelines(
            [
                # This has to be first line.
                f"{indent}{slashes}{title}\n",
                f"{subindent}protocol: {protocol}\n",
                f"{subindent}path: boot():/managarm/{eir}\n",
            ]
        )
        if protocol in {"limine", "multiboot2"}:
            self.out.write(f"{subindent}module_path: boot():/managarm/initrd.cpio\n")

        cmdlines = []
        if self.base_cmdline:
            cmdlines.append(self.base_cmdline)
        if extra_cmdline:
            cmdlines.append(extra_cmdline)
        cmdline = " ".join(cmdlines)
        if cmdline:
            self.out.write(f"{subindent}cmdline: {cmdline}\n")


def name_of_protocol(protocol):
    return {
        "limine": "Limine",
        "linux": "Linux",
        "multiboot2": "MB2",
        "efi": "UEFI",
    }[protocol]


def make_default_entries(writer, *, protocol):
    writer.write_entry(
        f"Weston (via {name_of_protocol(protocol)})",
        protocol=protocol,
    )
    writer.write_entry(
        f"kmscon (via {name_of_protocol(protocol)})",
        protocol=protocol,
        extra_cmdline="systemd.unit=kmscon.target",
    )


def make_extra_entries(writer, *, protocol):
    writer.write_entry(
        f"Profiling (via {name_of_protocol(protocol)})",
        protocol=protocol,
        extra_cmdline="kernel-profile",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=str)
    parser.add_argument(
        "--arch",
        choices=["x86_64", "aarch64", "riscv64"],
        required=True,
    )

    args = parser.parse_args()

    with open(args.out, "w") as f:
        writer = Writer(f)
        if args.arch == "x86_64":
            writer.base_cmdline = "bochs"
        else:
            writer.base_cmdline = "serial"

        writer.write_header()

        limine_available = args.arch in {"x86_64", "riscv64"}
        linux_available = args.arch in {"aarch64", "riscv64"}
        mb2_available = args.arch in {"x86_64"}

        # TODO: On RISC-V, we probably want to switch to eir-uefi but that is currently broken.
        if args.arch in {"x86_64", "riscv64"}:
            # Limine can be loaded either by UEFI or by BIOS on x86.
            # We can either use the Limine protocol or MB2 to cover both cases.
            default_protocol = "limine"
        else:
            # Since Limine itself must be loaded by UEFI on non-x86,
            # we can default to chainloading.
            default_protocol = "efi"

        with writer.submenu("+Managarm: default options"):
            make_default_entries(writer, protocol=default_protocol)

        with writer.submenu("Managarm: extra options"):
            make_extra_entries(writer, protocol=default_protocol)

        if default_protocol != "efi":
            with writer.submenu("Managarm: UEFI chainload"):
                make_default_entries(writer, protocol="efi")

        if limine_available and default_protocol != "limine":
            with writer.submenu("Managarm: Limine protocol"):
                make_default_entries(writer, protocol="limine")

        if linux_available:
            with writer.submenu("Managarm: Linux protocol"):
                make_default_entries(writer, protocol="linux")

        if mb2_available:
            with writer.submenu("Managarm: Multiboot2 protocol"):
                make_default_entries(writer, protocol="multiboot2")


if __name__ == "__main__":
    main()
