#!/usr/bin/env python3

import argparse
import errno
import functools
import io
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
from dataclasses import dataclass, field
from enum import Enum
from os import path
from typing import Dict, List

elevation_method = None
verbose = False
MANAGARM_ROOT_PART_TYPE = "64212B3B-56A1-4DFB-971E-BC8CD027996A"
EFI_SYSTEM_PART_TYPE = "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
global_mount_info = None
sfdisk_command = None


class MountInfo:
    def __init__(self, blockdev, mount_using, image, mountpoint, root_idx, efi_idx, root_uuid):
        self.blockdev = blockdev
        self.mount_using = mount_using
        self.image = image
        self.mountpoint = mountpoint
        self.root_idx = root_idx
        self.efi_idx = efi_idx
        self.root_uuid = root_uuid


class Partition:
    def __init__(self, idx, type, uuid, size):
        self.idx = idx
        self.type = type
        self.uuid = uuid
        self.size = size


# shlex.join is only available since Python 3.8
def join_command(args):
    return " ".join(shlex.quote(x) for x in args)


def run_elevated(cmd, stdin=None, capture_output=True):
    actual_cmd = [elevation_method] + cmd

    if elevation_method == "su":
        actual_cmd = [elevation_method, "-c", join_command(cmd)]

    if verbose:
        print(f'update-image: Running "{join_command(cmd)}" as root')

    res = subprocess.run(actual_cmd, capture_output=capture_output, input=stdin, encoding="utf-8")

    if res.returncode != 0:
        if capture_output:
            stderr = res.stderr.rstrip()
            raise RuntimeError(
                f'Command "{cmd[0]} ..." failed with code {res.returncode} and stderr:'
                f" {stderr}"
            )
        else:
            raise RuntimeError(f'Command "{cmd[0]} ..." failed with code {res.returncode}')

    return res.stdout.rstrip() if capture_output else ""


def run_regular(cmd, stdin=None, capture_output=True):
    if verbose:
        print(f'update-image: Running "{join_command(cmd)}"')

    res = subprocess.run(cmd, capture_output=capture_output, input=stdin, encoding="utf-8")

    if res.returncode != 0:
        if capture_output:
            stderr = res.stderr.rstrip()
            raise RuntimeError(
                f'Command "{cmd[0]} ..." failed with code {res.returncode} and stderr:'
                f" {stderr}"
            )
        else:
            raise RuntimeError(f'Command "{cmd[0]} ..." failed with code {res.returncode}')

    return res.stdout.rstrip() if capture_output else ""


def try_find_command_exec(command):
    i = shutil.which(command)
    if i:
        return i

    i = shutil.which(command, path="/usr/local/sbin:/usr/sbin:/sbin")
    if i:
        return i

    try:
        whereis_out = run_regular(["whereis", "-b", command]).split(" ")
        if len(whereis_out) > 1:
            if path.basename(whereis_out[1]) == command:
                return whereis_out[1]
            print(f"update-image: whereis returned a weird result: {whereis_out}")
    except RuntimeError:
        pass

    raise RuntimeError(f"Couldn't find {command} (tried looking in PATH and using whereis)")


def check_if_running(pid):
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False

    return True


def get_partition_list(image):
    image_needs_root = not os.access(image, os.R_OK, effective_ids=True)
    cmd = [sfdisk_command, "-d", image]
    out = run_elevated(cmd) if image_needs_root else run_regular(cmd)

    partitions = []

    for line in out.split("\n"):
        if line.startswith(image):
            name, params = line.split(" : ")
            toks = params.split(", ")
            type_param = [i for i in toks if i.startswith("type=")]
            uuid_param = [i for i in toks if i.startswith("uuid=")]
            size_param = [i for i in toks if i.startswith("size=")]

            if len(type_param) != 1 or len(uuid_param) != 1 or len(size_param) != 1:
                continue

            type = type_param[0][5:]
            uuid = uuid_param[0][5:]
            size = int(size_param[0][5:])
            idx = name[len(image) :]

            partitions.append(Partition(idx, type, uuid, size))

    return partitions


def dev_for_mountpoint(mountpoint):
    mnt = json.loads(run_regular(["findmnt", "--json", mountpoint]))
    partdev = mnt["filesystems"][0]["source"]
    diskdev = run_regular(["lsblk", "-no", "pkname", partdev])

    return (diskdev, partdev)


class MountAction:
    def __init__(self, mount_using, image, mountpoint, sysroot):
        self.mount_using = mount_using
        self.image = image
        self.mountpoint = mountpoint
        self.sysroot = sysroot

    def run(self):
        global global_mount_info

        partitions = get_partition_list(self.image)

        diskdev = self.image
        root_partition = None
        root_uuid = None
        efi_partition = None
        for part in partitions:
            if part.type == MANAGARM_ROOT_PART_TYPE:
                root_partition = part.idx
                root_uuid = part.uuid
            elif part.type == EFI_SYSTEM_PART_TYPE:
                efi_partition = part.idx
                # image_create creates a 256MiB ESP partition, while older images
                # have an ESP that's only 16MiB large.
                if part.size < (128 * 1024 * 1024 / 512):
                    raise RuntimeError("Your image's EFI partition is too small. "
                                       "Update the image_create tool and recreate the image...")

        if global_mount_info:
            if not os.access(global_mount_info.blockdev, os.F_OK, effective_ids=True):
                print(
                    "update-image: Mount info exists, but refers to a nonexistent block"
                    " device, ignoring."
                )
                try:
                    script_dir = os.path.realpath(os.path.dirname(sys.argv[0]))
                    os.remove(os.path.join(script_dir, "update-image-mount-info"))
                except FileNotFoundError:
                    pass
                global_mount_info = None
            else:
                print("update-image: The image appears to already be mounted (mount info exists)")
                return

        if not efi_partition:
            raise RuntimeError("No suitable EFI system partition found")

        if not root_partition:
            raise RuntimeError("No suitable root partition found")

        if verbose:
            print(f"update-image: EFI partition is partition no. {efi_partition}")
            print(f"update-image: Root partition is partition no. {root_partition}")

        if self.mount_using == "loopback":
            diskdev = run_elevated(["losetup", "-Pf", "--show", self.image])
            if verbose:
                print(f'update-image: "{self.image}" mounted as "{diskdev}"')

        if self.mount_using == "block" or self.mount_using == "loopback":
            # Handle both /dev/sdXY and /dev/nvmeXpY etc correctly
            sep = ""
            if diskdev[-1].isdigit():
                sep = "p"

            try:
                os.mkdir(self.mountpoint)
            except FileExistsError:
                pass
            run_elevated(["mount", f"{diskdev}{sep}{root_partition}", self.mountpoint])
        elif self.mount_using == "guestfs":
            # guestfs requires us to specify all mountpoints at once
            args = [
                "guestmount",
                "--pid-file",
                "guestfs.pid",
                "-a",
                self.image,
                "-m",
                f"/dev/sda{root_partition}",
            ]

            args += ["-m", f"/dev/sda{efi_partition}:/boot"]

            args.append(self.mountpoint)

            try:
                os.mkdir(self.mountpoint)
            except FileExistsError:
                pass
            run_regular(args)
        elif self.mount_using == "docker":
            cmds = "mkdir /devtmpfs\n"
            cmds += "mount -t devtmpfs devtmpfs /devtmpfs\n"
            cmds += 'BLOCKDEV=$(losetup -Pf --show image | sed "s/dev/devtmpfs/")\n'
            cmds += f'mount "$BLOCKDEV"p{root_partition} /mnt\n'
            cmds += f'mount "$BLOCKDEV"p{efi_partition} /mnt/boot\n'

            cmds += 'echo "$BLOCKDEV" > /stuff/scripts/tmp-docker-blockdev\n'
            cmds += "tail -f /dev/null"

            script_dir = os.path.realpath(os.path.dirname(sys.argv[0]))

            try:
                os.remove(os.path.join(script_dir, "tmp-docker-blockdev"))
            except FileNotFoundError:
                pass

            sysroot_dir = os.path.realpath(self.sysroot)
            initrd = os.path.realpath("initrd.cpio")
            tools_dir = os.path.realpath("tools")
            image = os.path.realpath(self.image)

            run_regular(
                [
                    "docker",
                    "run",
                    "--privileged=true",
                    "--rm",
                    "--name",
                    "managarm-mount",
                    "-v",
                    f"{sysroot_dir}:/stuff/system-root:ro",
                    "-v",
                    f"{initrd}:/stuff/initrd.cpio:ro",
                    "-v",
                    f"{tools_dir}:/stuff/tools:ro",
                    "-v",
                    f"{script_dir}:/stuff/scripts:rw",
                    "-v",
                    f"{image}:/stuff/image:rw",
                    "-w",
                    "/stuff",
                    "-u",
                    "root:root",
                    "-d",
                    "managarm-buildenv",
                    "bash",
                    "-c",
                    cmds,
                ]
            )

            while not os.access(os.path.join(script_dir, "tmp-docker-blockdev"), os.F_OK):
                pass

            with open(os.path.join(script_dir, "tmp-docker-blockdev")) as f:
                diskdev = f.read().rstrip()

            os.remove(os.path.join(script_dir, "tmp-docker-blockdev"))

            self.mountpoint = "/mnt inside of container"
        else:
            raise RuntimeError(f"Unknown mount method {self.mount_using}")

        if self.mount_using != "docker":
            efi_path = os.path.join(self.mountpoint, "boot")

            print(f"update-image: EFI partition exists, mounting to {efi_path}")
            if not os.path.isdir(efi_path):
                raise RuntimeError(
                    "/boot does not exist on mountpoint (or is not a directory)"
                )

            sep = ""
            if diskdev and diskdev[-1].isdigit():
                sep = "p"

            if self.mount_using == "block" or self.mount_using == "loopback":
                run_elevated(["mount", f"{diskdev}{sep}{efi_partition}", efi_path])

        global_mount_info = MountInfo(
            diskdev,
            self.mount_using,
            self.image,
            self.mountpoint,
            root_partition,
            efi_partition,
            root_uuid,
        )

        with open("update-image-mount-info", "w") as f:
            json.dump(global_mount_info.__dict__, f)

    def name(self):
        return "mount"

    def details(self):
        return f'mount ("{self.image}" to "{self.mountpoint}" using {self.mount_using})'


FsAction = Enum("FsAction", "CREATE_DIR ENSURE_LINKS INSTALL CP CP_SED RSYNC")


def generate_plan(arch, root_uuid, scriptdir):

    for x in [
        "root",
        "usr/bin",
        "usr/lib",
        "var",
        "dev",
        "proc",
        "run",
        "sys",
        "tmp",
        "home",
        "boot",
        "boot/grub",
        "boot/managarm",
    ]:
        yield FsAction.CREATE_DIR, x

    yield FsAction.ENSURE_LINKS

    yield FsAction.INSTALL, "initrd.cpio", "boot/managarm", dict(ignore_sysroot=True)

    if arch == "x86_64-managarm":
        yield FsAction.INSTALL, "usr/managarm/bin/eir-mb2", "boot/managarm"
        yield FsAction.INSTALL, "usr/managarm/bin/eir-uefi", "boot/managarm"
        yield FsAction.INSTALL, "usr/managarm/bin/thor", "boot/managarm"
        yield FsAction.CP_SED, os.path.join(scriptdir, "grub.cfg"), \
            "boot/grub/", "@ROOT_UUID@", root_uuid

        yield (
            FsAction.CP,
            "system-root/usr/share/limine/BOOTX64.EFI",
            "boot/EFI/BOOT",
        )

        yield FsAction.CP_SED, os.path.join(
            scriptdir, "limine.conf"
        ), "boot/", "@ROOT_UUID@", root_uuid
    elif arch == "aarch64-managarm":
        # TODO(qookie): Install an appropriate eir once we have one
        yield FsAction.INSTALL, "usr/managarm/bin/thor", "boot/managarm"

        yield (
            FsAction.CP,
            "system-root/usr/share/limine/BOOTAA64.EFI",
            "boot/EFI/BOOT",
        )

        yield FsAction.CP_SED, os.path.join(
            scriptdir, "limine.conf"
        ), "boot/", "@ROOT_UUID@", root_uuid

    yield FsAction.RSYNC, "bin"
    yield FsAction.RSYNC, "lib"
    yield FsAction.RSYNC, "sbin"
    yield FsAction.RSYNC, "root/"
    yield FsAction.RSYNC, "usr/"
    yield FsAction.RSYNC, "etc/"
    yield FsAction.RSYNC, "var/"
    yield FsAction.RSYNC, "home/"


def ensure_sysroot_links(sysroot):
    for x in ["bin", "lib", "sbin"]:
        wanted_link = os.path.join(sysroot, x)
        if not os.path.islink(wanted_link):
            print(f"{wanted_link} is not a symlink, aborting...")
            raise RuntimeError("Broken sysroot, please fix this manually and rerun this script")


def iterate_plan(plan, callbacks):
    for _act in plan:
        kwargs = {}
        if isinstance(_act, tuple):
            args = list(_act)  # lists have extra operations
        else:
            args = [_act]  # single argument
        cmd = args.pop(0)
        if args and isinstance(args[-1], dict):
            kwargs = args.pop(-1)

        fn = callbacks.get(cmd, None)
        assert fn, f"action {cmd} not implemented"
        fn(*args, **kwargs)


class UpdateFsAction:
    def __init__(self, mountpoint, sysroot, arch):
        self.mountpoint = mountpoint
        self.sysroot = sysroot
        self.arch = arch

    def run(self):
        root_uuid = None
        is_docker = False
        needs_root = False
        target_mntpoint = self.mountpoint
        scriptdir = os.path.dirname(sys.argv[0])

        if global_mount_info:
            root_uuid = global_mount_info.root_uuid

            if global_mount_info.mount_using == "docker":
                target_mntpoint = "/mnt"
                scriptdir = "/stuff/scripts"
                is_docker = True
            else:
                needs_root = not global_mount_info.mount_using == "guestfs"
        else:
            # Determine root uuid manually for mountpoint
            diskdev, partdev = dev_for_mountpoint(self.mountpoint)

            if os.path.isdir("/dev/disk/by-uuid"):
                for diskuuid in os.listdir("/dev/disk/by-uuid"):
                    part = os.path.realpath(f"/dev/disk/by-uuid/{diskuuid}")
                    if part == partdev:
                        root_uuid = uuid
                        break

            if not root_uuid:
                partitions = get_partition_list(diskdev)

                if diskdev[-1].isdigit():
                    diskdev += "p"

                idx = int(partdev[len(diskdev) :])

                for part in partitions:
                    if part.idx == idx:
                        root_uuid = part.uuid
                        break

            if verbose:
                print(f'update-image: Determined UUID for "{self.mountpoint}" is' f" {root_uuid}")

            needs_root = not os.access(target_mntpoint, os.W_OK, effective_ids=True)

        print(
            "update-image: Updating the image",
            "requires" if needs_root else "doesn't require",
            "root",
        )

        steps = [["set", "-ex"]]

        def plan_create_dir(dir):
            steps.append(["mkdir", "-p", os.path.join(target_mntpoint, dir)])

        def plan_install(source, dest, ignore_sysroot=False):
            if not ignore_sysroot:
                source = os.path.join(self.sysroot, source)
            target = os.path.join(target_mntpoint, dest)

            steps.append(["install", source, target])

        def plan_rsync(dir):
            source = os.path.join(self.sysroot, dir)
            target = os.path.join(target_mntpoint, dir)
            steps.append(["rsync", "-a", "--delete", source, target])

        def plan_cp(source, dest):
            target = os.path.join(target_mntpoint, dest)
            steps.append(["cp", source, target])

        def plan_cp_sed(source, dest, pattern, replace):
            _, name = os.path.split(source)
            target = os.path.join(target_mntpoint, dest, name)
            steps.append(["cp", source, target])
            steps.append(["sed", "-i", f"s|{pattern}|{replace}|g", target])

        def plan_ensure_links():
            ensure_sysroot_links(self.sysroot)

        iterate_plan(
            generate_plan(self.arch, root_uuid, scriptdir),
            {
                FsAction.CREATE_DIR: plan_create_dir,
                FsAction.ENSURE_LINKS: plan_ensure_links,
                FsAction.INSTALL: plan_install,
                FsAction.CP: plan_cp,
                FsAction.CP_SED: plan_cp_sed,
                FsAction.RSYNC: plan_rsync,
            },
        )

        print("update-image: Updating the file system...")

        commands = "\n".join([join_command(step) for step in steps])

        if is_docker:
            run_regular(
                ["docker", "exec", "-i", "-u", "root:root", "managarm-mount", "bash"],
                commands,
                False,
            )
        elif needs_root:
            run_elevated(["bash"], commands, False)
        else:
            run_regular(["bash"], commands, False)

        print("update-image: Done")

    def name(self):
        return "update file system"

    def details(self):
        return f'update file system (from "{self.sysroot}" to "{self.mountpoint}")'


class UnmountAction:
    def __init__(self):
        pass

    def run(self):
        global global_mount_info

        if not global_mount_info:
            raise RuntimeError("File system not mounted")

        blockdev = global_mount_info.blockdev
        mount_using = global_mount_info.mount_using
        mountpoint = global_mount_info.mountpoint

        efi_path = os.path.join(mountpoint, "boot")
        if mount_using == "block" or mount_using == "loopback":
            run_elevated(["umount", "-l", efi_path])

        if mount_using == "loopback":
            run_elevated(["losetup", "-d", f"{blockdev}"])

        if mount_using == "block" or mount_using == "loopback":
            run_elevated(["umount", "-l", mountpoint])
        elif mount_using == "guestfs":
            run_regular(["guestunmount", mountpoint])

            with open("guestfs.pid", "r") as pidfile:
                pid = int(pidfile.read().rstrip())
                for _ in range(10):
                    if check_if_running(pid):
                        time.sleep(0.1)

                while check_if_running(pid):
                    time.sleep(1)
        elif mount_using == "docker":
            cmds = "sync\n"
            cmds += "umount /mnt/boot\n"
            cmds += "umount /mnt\n"
            cmds += f"losetup -d {blockdev}\n"
            cmds += "umount /devtmpfs"

            run_regular(
                [
                    "docker",
                    "exec",
                    "-i",
                    "-u",
                    "root:root",
                    "managarm-mount",
                    "bash",
                    "-c",
                    cmds,
                ]
            )

            run_regular(["docker", "stop", "-t", "0", "managarm-mount"])
        else:
            raise RuntimeError(f"Unknown mount method {mount_using}")

        # Delete mount info
        os.remove("update-image-mount-info")
        global_mount_info = None

    def name(self):
        return "unmount"

    def details(self):
        if not global_mount_info:
            return "unmount (file system not mounted)"

        return (
            f'unmount ("{global_mount_info.mountpoint}" using' f" {global_mount_info.mount_using})"
        )


def add_dest_basename(src, dst):
    if dst[-1] == '/':
        dst += os.path.basename(src)
    return dst


def _is_boot(x):
    return (
        (x.startswith("boot/") or x.startswith("/boot/"))
        and (len(x) > 6 if x[0] == '/' else len(x) > 5)
    )


def logged_run(cmd, *args, **kwargs):
    print("update-image: running program: " + shlex.join(cmd))
    return subprocess.run(cmd, *args, **kwargs)


def logged_check_call(cmd, *args, **kwargs):
    return logged_run(cmd, check=True, *args, **kwargs)


@dataclass
class RemakeImageAction:
    """
    This action remakes the filesystems in the image directly from the sysroot.
    This approach turns out to be extremely quick and efficient, but does require
    modifying the host sysroot directory.
    """

    image: str
    mountpoint: str
    sysroot: str
    arch: str

    _boot_files: Dict[str, bytes] = field(default_factory=dict, init=False)
    _boot_dirs: List[str] = field(default_factory=list, init=False)

    def _create_dir(self, x):
        if _is_boot(x):
            self._boot_dirs.append(x)
        else:
            os.makedirs(os.path.join(self.sysroot, x), exist_ok=True)

    def _ensure_links(self):
        ensure_sysroot_links(self.sysroot)

    def _install(self, src, dst, ignore_sysroot=False):
        if not ignore_sysroot:
            src = os.path.join(self.sysroot, src)
        if _is_boot(add_dest_basename(src, dst)):
            with tempfile.NamedTemporaryFile('r+b') as tmpf:
                actual_src = src

                # XXX(arsen): I assume the path provided is a dir
                dst = os.path.join(dst, os.path.basename(src))
                with open(actual_src, "rb") as fsrc:
                    self._boot_files[dst] = fsrc.read()
                    return

        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))

        dst = os.path.join(self.sysroot, dst)
        if os.path.samefile(src, dst):
            return

        installargs = ["install"]

        installargs += [src, dst]
        logged_check_call(installargs)

    def _cp_sed(self, src, dst, var, val):
        if _is_boot(add_dest_basename(src, dst)):
            dstopen = io.BytesIO
            if dst.endswith("/"):
                dst = os.path.join(dst, os.path.basename(src))
            dst = os.path.normpath("/" + dst)
        else:
            dst = os.path.join(self.sysroot, dst)
            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))
            dstopen = functools.partial(open, dst, "wb")
        var = var.encode("utf-8")
        val = val.encode("utf-8")

        with open(src, "rb") as fsrc, dstopen() as fdst:
            while chunk := fsrc.read(32768):
                # XXX(arsen): edge case: if @VAR@ is on a 32kB boundary, this will fail.
                #             files we currently substitute on are very small, so this
                #             shouldn't be problematic
                fdst.write(chunk.replace(var, val))

            if isinstance(fdst, io.BytesIO):
                self._boot_files[dst] = fdst.getvalue()

    def run(self):
        if not os.access(self.image, os.W_OK | os.R_OK):
            raise RuntimeError(f"{self.image} does not exist or is not r/w accessible")

        scriptdir = os.path.dirname(sys.argv[0])

        # start by correcting the sysroot slightly
        root_uuid = str(uuid.uuid4())
        iterate_plan(
            generate_plan(self.arch, root_uuid, scriptdir),
            {
                FsAction.CREATE_DIR: self._create_dir,
                FsAction.ENSURE_LINKS: self._ensure_links,
                FsAction.INSTALL: self._install,
                FsAction.CP: functools.partial(self._install, ignore_sysroot=True),
                FsAction.CP_SED: self._cp_sed,
                FsAction.RSYNC: lambda *a, **kw: None,  # ignored
            },
        )

        def setup_rootfs(start, size):
            cmd = [
                mke2fs_command,
                "-Ft",
                "ext2",
                "-M",
                "/",
                "-L",
                "managarm_rootfs",
                "-U",
                root_uuid,
                "-d",
                "system-root/",
                "-E",
                # XXX: is 512 correct?
                "offset={}".format(512 * start),
                self.image,
                "{}K".format(size // 1024),
            ]
            logged_check_call(cmd)

        def setup_esp(start, size):
            # image_create creates a 256MiB ESP partition, while older images
            # have an ESP that's only 16MiB large.
            if size < (128 * 1024 * 1024):
                raise RuntimeError("Your image's EFI partition is too small. "
                                   "Update the image_create tool and recreate the image...")

            # create the ESP
            cmd = [
                mkfsvfat_command,
                "-F",
                "32",
                "-n",
                "ESP",
                "-s",
                "2",
                "-S",
                "512",
                "--offset",
                str(start),
                self.image,
                str(size // 1024),
            ]
            logged_check_call(cmd)

            # manipulate it using mtools
            dosimg = "{}@@{}".format(self.image, start * 512)
            # create \EFI\BOOT
            logged_check_call(["mmd", "-i", dosimg, "EFI"])
            logged_check_call(["mmd", "-i", dosimg, "EFI/BOOT"])

            # ... and populate it, first with directories ...
            for dir in self._boot_dirs:
                if dir.startswith("/"):
                    dir = dir[1:]
                dir = dir[len("boot") :]
                logged_check_call(["mmd", "-i", dosimg, dir])
            # ... then with files
            for file, val in self._boot_files.items():
                if file.startswith("/"):
                    file = file[1:]
                file = file[len("boot") :]
                logged_check_call(["mcopy", "-i", dosimg, "-", f"::{file}"], input=val)

        part_lines = (
            logged_run(
                ["partx", "-gbs", "--output", "start,size,type", self.image],
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .splitlines()
        )

        done_make = False
        for part_line in part_lines:
            [start, size, parttype] = [x for x in part_line.split(" ") if x]

            setup_fn = {
                MANAGARM_ROOT_PART_TYPE: setup_rootfs,
                EFI_SYSTEM_PART_TYPE: setup_esp,
            }.get(
                parttype.upper(), lambda x, y: None
            )  # noop default

            done_make = True
            setup_fn(int(start), int(size))

        if not done_make:
            raise RuntimeError(f"couldn't find any partitions in {self.image}")

    def name(self):
        return "remake"

    def details(self):
        return f"remake {self.image} from scratch"


def make_action(name, mount_using, image, mountpoint, sysroot, arch):
    if name == "mount":
        return MountAction(mount_using, image, mountpoint, sysroot)
    elif name == "update-fs":
        return UpdateFsAction(mountpoint, sysroot, arch)
    elif name == "unmount":
        return UnmountAction()
    elif name == "remake":
        return RemakeImageAction(image, mountpoint, sysroot, arch)
    else:
        raise RuntimeError(f"Unknown action {name}")


def determine_elevation_method(method):
    if method != "auto" and shutil.which(method):
        return method

    for i in ["sudo", "doas", "su"]:
        if shutil.which(i):
            return i

    raise RuntimeError("No method to elevate permissions found")


class Plan:
    def __init__(self, actions):
        self.actions = actions
        self.error_count = 0

    def print(self):
        print("update-image: Running the following plan:")
        for action in self.actions:
            print(f" - {action.name()}")

    def run(self):
        for action in self.actions:
            print(f"update-image: Running action {action.details()}")
            try:
                action.run()
            except Exception:
                self.error_count += 1
                print(f"update-image: Action {action.name()} failed with:")
                traceback.print_exc()


parser = argparse.ArgumentParser(description="Update a managarm installation")
parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
parser.add_argument(
    "-m",
    "--mount-using",
    dest="mount_using",
    choices=["loopback", "docker", "guestfs", "block"],
    default="guestfs",
    help="How to mount the image (default: guestfs)",
)
parser.add_argument(
    "-i",
    "--with-image",
    dest="image_path",
    metavar="image",
    type=str,
    default="image",
    help="Path to image (default: image)",
)
parser.add_argument(
    "-M",
    "--with-mount-point",
    dest="mountpoint_path",
    metavar="mountpoint",
    type=str,
    default="mountpoint",
    help="Path to mount point (default: mountpoint)",
)
parser.add_argument(
    "-s",
    "--with-sysroot",
    dest="sysroot_path",
    metavar="sysroot",
    type=str,
    default="system-root",
    help="Path to system root (default: system-root)",
)
parser.add_argument(
    "-e",
    "--elevate-with",
    dest="elevate_with",
    choices=["sudo", "doas", "su", "auto"],
    default="auto",
    help="How to run commands as root (required for loopback and block, default: auto)",
)
parser.add_argument(
    "-t",
    "--triple",
    dest="arch",
    choices=["x86_64-managarm", "aarch64-managarm"],
    default="x86_64-managarm",
    help="Target system triple (needed for the update-fs step, default: x86_64-managarm)",
)
parser.add_argument(
    "plan",
    metavar="action",
    nargs="*",
    choices=[[], "mount", "update-fs", "unmount", "remake"],
    help=(
        "Action to run (one of: mount, update-fs, unmount, remake).\n"
        "The default list of actions is [mount, update-fs, unmount]"
    ),
)

args = parser.parse_args()

action_list = ["mount", "update-fs", "unmount"]
if len(args.plan):
    action_list = args.plan

verbose = args.verbose
elevation_method = determine_elevation_method(args.elevate_with)

if verbose:
    print("update-image: Being extra verbose")
    print(f'update-image: Using "{elevation_method}" for permission elevation')

try:
    with open("update-image-mount-info", "r") as f:
        info = json.load(f)
        global_mount_info = MountInfo(
            info["blockdev"],
            info["mount_using"],
            info["image"],
            info["mountpoint"],
            info["root_idx"],
            info["efi_idx"],
            info["root_uuid"],
        )
except (FileNotFoundError, json.JSONDecodeError):
    pass

sfdisk_command = try_find_command_exec("sfdisk")
mkfsvfat_command = try_find_command_exec("mkfs.vfat")
mke2fs_command = try_find_command_exec("mke2fs")

if verbose:
    print(f'update-image: Found sfdisk at "{sfdisk_command}"')

plan = Plan(
    [
        make_action(
            v,
            args.mount_using,
            args.image_path,
            args.mountpoint_path,
            args.sysroot_path,
            args.arch,
        )
        for v in action_list
    ]
)
plan.print()
plan.run()

print("update-image: Finished running plan.")
if plan.error_count > 0:
    print(f"update-image: {plan.error_count} step(s) failed.")
    sys.exit(1)
