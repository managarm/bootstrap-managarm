#!/usr/bin/env python3

import asyncio
import argparse
import base64
import contextlib
import enum
import json
import os
import re
import shlex
import shutil
import subprocess
import string
import struct
import socket
import sys
import pathlib
import time
import tempfile
import yaml

main_parser = argparse.ArgumentParser()
main_subparsers = main_parser.add_subparsers()

def which(cmd):
    path = shutil.which(cmd)
    if path is not None:
        return path
    path = shutil.which(cmd, path="/usr/local/sbin:/usr/sbin:/sbin")
    if path is not None:
        return path
    raise FileNotFoundError(f"Could not find executable: {cmd}")

# ---------------------------------------------------------------------------------------
# qemu subcommand.
# ---------------------------------------------------------------------------------------

def qemu_check_device(qemu, args, dev):
    out = subprocess.check_output([qemu] + args + ["-device", "?"], encoding="ascii")
    for line in out.splitlines():
        if line.startswith(f"name \"{dev}\""):
            return True
    print("QEMU does not support device {}".format(dev), file=sys.stderr)
    sys.exit(1)

def qemu_check_nic(qemu, args, nic):
    out = subprocess.check_output([qemu] + args + ["-nic", "?"], encoding="ascii")
    for line in out.splitlines():
        if line == nic:
            return True
    print("QEMU does not support {} NICs".format(nic), file=sys.stderr)
    sys.exit(1)

def qemu_process_usb_passthrough(device, pcap):
    usb_aliases = {
        "cp2102": "10c4:ea60",
        "ft232": "0403:6001",
        "ax88179": "0b95:1790",
    }

    if device.casefold() in usb_aliases:
        devid = usb_aliases[device.casefold()]
    else:
        devid = device

    if (len(devid) != 9 or devid[4] != ':'
        or not all(c in string.hexdigits for c in devid[0:4])
        or not all(c in string.hexdigits for c in devid[5:9])):

        print(f"Invalid USB passthrough device '{devid}'")
        sys.exit(1)

    out = subprocess.check_output([
        "udevadm", "trigger", "--verbose", "--dry-run", "--subsystem-match=usb",
        f"--attr-match=idVendor={devid[0:4]}", f"--attr-match=idProduct={devid[5:9]}"
    ]).splitlines()

    if len(out) < 1:
        print(f"USB passthrough device {devid} not found")
        sys.exit(1)

    attrs = subprocess.check_output(["udevadm", "info", out[0]]).splitlines()
    uaccess_verified = False
    for attr in attrs:
        if not attr.startswith(b"E: CURRENT_TAGS="):
            continue
        if b"uaccess" in attr:
            uaccess_verified = True
            break

    if not uaccess_verified:
        print(f"USB passthrough device {devid} is not tagged 'uaccess' in udev")
        sys.exit(1)

    devstr = f"usb-host,vendorid=0x{devid[0:4]},productid=0x{devid[5:9]}"

    if pcap:
        devstr += f",pcap={device}.pcap"

    return ["-device", devstr]

qemu_pci_bridges = 0

def qemu_parse_device_spec(yml):
    args = []

    def parse_device(yml, *, bus_id=None, device_id=None):
        global qemu_pci_bridges

        args = []
        devtype = yml.get('type', 'device')

        print(f"Constructing '{yml['name']}' of type '{devtype}'")

        if devtype == 'pci-bridge':
            qemu_pci_bridges += 1
            properties = f"pci-bridge,id={yml['name']},chassis_nr={qemu_pci_bridges}"
            if bus_id:
                properties += f',bus={bus_id}'
            args += ['-device', properties]

            for i, device in enumerate(yml.get('devices', [])):
                args += parse_device(device, bus_id=yml['name'], device_id=i)
        elif devtype == 'pci-multifunction-device':
            multifunction_property_set = False

            for i, func in enumerate(yml.get('functions', [])):
                properties = f"vfio-pci,host={func['host']}"
                if bus_id:
                    properties += f',bus={bus_id}'
                if i == 0:
                    properties += ',multifunction=on'
                assert device_id is not None
                properties += f',addr={device_id:02x}.{i}'
                args += ['-device', properties]
        elif devtype == 'pci-device':
            args += ['-device', f"vfio-pci,host={yml['host']},id={yml['name']}"]
        elif devtype == 'ehci':
            properties = f"usb-ehci,id={yml['name']}"
            if bus_id:
                properties += f',bus={bus_id}'
            args += ['-device', properties]
        elif devtype == 'xhci':
            properties = f"qemu-xhci,id={yml['name']}"
            if bus_id:
                properties += f',bus={bus_id}'
            args += ['-device', properties]
        elif devtype == 'uhci':
            properties = f"piix3-usb-uhci,id={yml['name']}"
            if bus_id:
                properties += f',bus={bus_id}'
            args += ['-device', properties]
        else:
            print(f"error: unsupported device-spec device kind {devtype}")
            sys.exit(1)

        return args

    for device in yml:
        args += parse_device(device)

    return args

def setup_tftp_directory():
    tftp_dir = tempfile.TemporaryDirectory(suffix=".tftp.d", delete=True)

    shutil.copytree("packages/limine/usr/share/limine/", tftp_dir.name, dirs_exist_ok=True)
    shutil.copytree("packages/managarm-kernel/usr/managarm/bin/", os.path.join(tftp_dir.name, "managarm"), dirs_exist_ok=True)
    shutil.copytree("packages/managarm-kernel-uefi/usr/managarm/bin/", os.path.join(tftp_dir.name, "managarm"), dirs_exist_ok=True)
    shutil.copyfile("initrd.cpio", os.path.join(tftp_dir.name, "managarm", "initrd.cpio"))
    shutil.copyfile("../src/scripts/nvme-of-boot.conf", os.path.join(tftp_dir.name, "limine.conf"))
    return tftp_dir

class TftpServer:
    def __init__(self, args):
        self.verbose = args.verbose

    class TftpOpcode(enum.Enum):
        RRQ = 1
        WRQ = 2
        DATA = 3
        ACK = 4
        ERROR = 5
        OACK = 6

    class TftpErrorCode(int, enum.Enum):
        NotDefined = 0
        FileNotFound = 1
        AccessViolation = 2
        DiskFull = 3
        IllegalOperation = 4
        UnknownTransfer = 5
        FileExists = 6
        NoSuchUser = 7

    class ReadRequest:
        def __init__(self, buf):
            self.opcode = TftpServer.TftpOpcode(struct.unpack(">H", buf[:2])[0])

            if self.opcode != TftpServer.TftpOpcode.RRQ:
                raise ValueError(f"Invalid opcode {self.opcode}")

            self.filename = buf[2:].split(b"\0", 1)[0].decode("ascii")
            self.mode = buf[(len(self.filename) + 3):].split(b"\0", 1)[0].decode("ascii").lower()

            self.opts = False
            self.tsize = None
            self.blksize = None
            self.windowsize = None

            if self.mode and self.mode not in ("octet", "netascii"):
                raise ValueError(f"Invalid mode {self.mode}")

            options_offset = 2 + len(self.filename) + 1 + len(self.mode) + 1
            self.acknowledged_opts = b""

            while True:
                option = buf[options_offset:].split(b"\0", 1)[0].decode("ascii")
                if not option:
                    break
                if option not in ("blksize", "tsize", "windowsize"):
                    raise ValueError(f"Unsupported option {option}")

                option_value = buf[options_offset + len(option) + 1:].split(b"\0", 1)[0].decode("ascii")
                self.opts = True

                if option == "tsize":
                    self.tsize = int(option_value)
                elif option == "blksize":
                    self.blksize = int(option_value)
                elif option == "windowsize":
                    self.windowsize = int(option_value)

                options_offset += len(option) + 1 + len(option_value) + 1

        def get_blksize(self):
            return self.blksize or 512

        def get_options_ack(self, f):
            res = b""

            if self.tsize is not None:
                tsize_res = str(self.tsize) if self.tsize > 0 else str(f.stat().st_size)

                res += b"tsize\0" + tsize_res.encode("ascii") + b"\0"

            if self.blksize is not None:
                res += b"blksize\0" + str(self.blksize).encode("ascii") + b"\0"

            if self.windowsize is not None:
                res += b"windowsize\0" + str(self.windowsize).encode("ascii") + b"\0"

            return res

    class DataPacket:
        def __init__(self, block, data=b""):
            self.packet = struct.pack(">HH", TftpServer.TftpOpcode.DATA.value, block) + data

    class Error:
        def __init__(self, code=0, msg=None, buf=None):
            if buf:
                self.packet = buf
            else:
                self.packet = struct.pack(">HH", TftpServer.TftpOpcode.ERROR.value, code)
                if msg:
                    self.packet += bytes(msg, "ascii")
                self.packet += b"\0"

        @property
        def code(self) -> int:
            return struct.unpack(">H", self.packet[2:4])[0]

        @property
        def message(self) -> str:
            return self.packet[4:].split(b"\0", 1)[0].decode("ascii")

    class OptionsAck:
        def __init__(self, request, file):
            self.packet = struct.pack(">H", TftpServer.TftpOpcode.OACK.value) + request.get_options_ack(file)

    def wait_for_ack(self, cs, block):
        while True:
            reply, _ = cs.recvfrom(516)
            opcode = TftpServer.TftpOpcode(struct.unpack(">H", reply[:2])[0])
            if opcode == TftpServer.TftpOpcode.ACK:
                ack_block = struct.unpack(">H", reply[2:])[0]
                if ack_block == block:
                    break
            elif opcode == TftpServer.TftpOpcode.ERROR:
                error = TftpServer.Error(buf=reply)
                raise ValueError(f"Received error code {error.code}: {error.message}")

    def run(self, tftp_root: tempfile.TemporaryDirectory):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", 69))

        while True:
            if self.verbose:
                print("Waiting for client connection")
            data, client = s.recvfrom(516)
            try:
                rrq = self.ReadRequest(data)
            except ValueError as e:
                print(f"Connection from {client[0]}:{client[1]} failed: {e}")
                s.sendto(TftpServer.Error(msg=str(e)).packet, client)
                continue;

            cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            cs.bind(("0.0.0.0", 0))
            if self.verbose:
                print(f"Serving client {client[0]}:{client[1]} on port {cs.getsockname()[1]}")

            root_path = pathlib.Path(tftp_root.name).resolve()
            file = pathlib.Path.joinpath(root_path, pathlib.Path(rrq.filename.removeprefix("/"))).resolve()

            if root_path not in file.parents:
                print(f"Client requested file outside of TFTP root: {rrq.filename}")
                cs.sendto(TftpServer.Error(code=2, msg="Access violation").packet, client)
                continue

            if not file.exists() or not file.is_file():
                print(f"Client requested non-existing file: {rrq.filename}")
                cs.sendto(TftpServer.Error(code=TftpServer.TftpErrorCode.FileNotFound, msg=f"File {rrq.filename} does not exist").packet, client)
                continue

            if rrq.opts:
                cs.sendto(TftpServer.OptionsAck(rrq, file).packet, client)

            if rrq.tsize == 0:
                continue

            if self.verbose:
                print(f"Client requested file: {file}")
            with open(file, "rb") as f:
                block = 1
                total_bytes = min(file.stat().st_size, rrq.tsize or file.stat().st_size)

                for _ in range(total_bytes // rrq.get_blksize()):
                    data = f.read(rrq.get_blksize())
                    cs.sendto(self.DataPacket(block, data).packet, client)
                    if self.verbose:
                        print(f"[{block}] {len(data)} bytes sent")

                    if not rrq.windowsize or block % rrq.windowsize == 0:
                        try:
                            self.wait_for_ack(cs, block)
                        except ValueError as e:
                            print(f"Client {client[0]}:{client[1]} failed to ACK: {e}")
                            continue

                    block += 1

                if total_bytes % rrq.get_blksize() != 0:
                    data = f.read()
                    cs.sendto(self.DataPacket(block, data).packet, client)
                    if self.verbose:
                        print(f"[{block}] {len(data)} bytes sent")

                    try:
                        self.wait_for_ack(cs, block)
                    except ValueError as e:
                        print(f"Client {client[0]}:{client[1]} failed to ACK: {e}")

                else:
                    cs.sendto(self.DataPacket(block).packet, client)
                    if self.verbose:
                        print(f"[{block}] 0 bytes sent")

                    try:
                        self.wait_for_ack(cs, block)
                    except ValueError as e:
                        print(f"Client {client[0]}:{client[1]} failed to ACK: {e}")

            if self.verbose:
                print("Transfer complete")
            cs.close()

class QemuRunner:
    def __init__(self, *, tmpdir, logfile=None, ci_script=None, ci_downloads=[]):
        self.tmpdir = tmpdir
        self.logfile = logfile
        self.ci_script = ci_script
        self.ci_downloads = ci_downloads
        self.proc = None
        self.launch_time = None
        self.last_io_time = None

        self.timeout = None
        self.io_timeout = None

    async def run(self, qemu, qemu_args, *, expect_all, expect_none):
        print("Running {}".format(shlex.join([qemu] + qemu_args)))
        self.proc = await asyncio.create_subprocess_exec(
            qemu,
            *qemu_args,
            stdout=subprocess.PIPE
        )
        self.launch_time = time.time()
        self.last_io_time = time.time()
        try:
            await asyncio.gather(
                self.do_wait(),
                self.process_stdout(expect_all=expect_all, expect_none=expect_none),
                self._do_ci_boot(),
            )
        finally:
            if self.proc.returncode is None:
                self.proc.terminate()

    async def do_wait(self):
        task = asyncio.create_task(self.proc.wait())

        pending = {task}
        while True:
            assert pending

            now = time.time()
            pending_timeouts = []
            if self.timeout is not None:
                pending_timeouts.append(self.timeout - (now - self.launch_time))
            if self.io_timeout is not None:
                pending_timeouts.append(self.io_timeout - (now - self.last_io_time))

            if not pending_timeouts:
                until_timeout = None
            else:
                until_timeout = min(pending_timeouts)
                if until_timeout < 0:
                    self.proc.terminate()
                    until_timeout = None

            done, pending = await asyncio.wait(pending, timeout=until_timeout)
            if done:
                break

    async def process_stdout(self, *, expect_all, expect_none):
        loop = asyncio.get_running_loop()
        w_transport, w_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
        writer = asyncio.StreamWriter(w_transport, w_protocol, None, loop)

        buf = bytes()
        while True:
            chunk = await self.proc.stdout.read(4096)
            if not chunk:
                break

            self.last_io_time = time.time()

            # Echo the chunk to stdout.
            if self.logfile:
                self.logfile.write(chunk)
            else:
                writer.write(chunk)
                await writer.drain()

            # Split the chunk into lines, analyze each line.
            buf += chunk
            while True:
                head, sep, tail = buf.partition(b"\n")
                if not sep:
                    break
                buf = tail
                try:
                    line = head.decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue

                if expect_all is not None:
                    expect_all = [expr for expr in expect_all if not expr.search(line)]
                    if not expect_all:
                        self.proc.terminate()
                for expr in expect_none:
                    if expr.search(line):
                        raise RuntimeError(f"Expected no line to be present that matches regexp '{expr.pattern}'")

        if expect_all is not None and expect_all:
            missing = ", ".join(f"'{expr.pattern}'" for expr in expect_all)
            raise RuntimeError(f"Expected lines matching regexps {missing}")

    async def _do_ci_boot(self):
        if self.ci_script is None:
            return

        debug = False

        socket_path = os.path.join(self.tmpdir, "serial.socket")
        while not os.path.exists(socket_path):
            await asyncio.sleep(0.1)
        (reader, writer) = await asyncio.open_unix_connection(socket_path)

        exitcode = None
        with contextlib.ExitStack() as stack:
            open_files = {}

            async for line in reader:
                contextlib.ExitStack

                msg = json.loads(line)
                m = msg["m"]
                if m == "ready":
                    if self.logfile or debug:
                        print("[vm-util] ci-boot is ready")
                    msg = {"m": "launch", "script": self.ci_script}
                    writer.write(json.dumps(msg).encode("utf8") + b"\n")

                    for file in self.ci_downloads:
                        print(f"[vm-util] requesting artifact '{file}' after script")
                        download = {"m": "download", "path": file}
                        writer.write(json.dumps(download).encode("utf8") + b"\n")
                    writer.write(json.dumps({"m": "done"}).encode("utf8") + b"\n")

                    await writer.drain()
                elif m == "download-data":
                    path = msg["path"]
                    if path in self.ci_downloads:
                        f = open_files.get(path)
                        if f is None:
                            f = stack.enter_context(open(os.path.basename(path), "wb"))
                            open_files[path] = f
                            print(f"[vm-util] downloading artifact '{path}'")

                        f.write(base64.b64decode(msg["data"]))
                    else:
                        print(f"[vm-util] unexpected download for file '{path}' supplied")
                elif m in {"stdout", "stderr"}:
                    data = base64.b64decode(msg["data"]).rstrip()
                    if self.logfile or debug:
                        print("[vm-util] ci-boot stdout: " + data.decode("utf8", errors="backslashreplace"))
                elif m == "exit":
                    exitcode = msg["exitcode"]
                    if self.logfile or debug:
                        print(f"[vm-util] ci-boot command exited with code {exitcode}")
                elif m == "done":
                    self.proc.terminate()
                elif m == "error":
                    text = msg["text"]
                    self.proc.terminate()
                    raise RuntimeError(f"ci-boot error: {text}")
                else:
                    print(f"[vm-util] ci-boot unknown packet: {m}")

        if exitcode is None:
            raise RuntimeError("ci-boot did not complete")
        if exitcode != 0:
            raise RuntimeError(f"ci-boot exited with code {exitcode}")

def do_qemu(args):
    # Default to --uefi for AArch64 and RISC-V.
    if args.arch == "riscv64" or args.arch == "aarch64":
        if args.uefi is None:
            args.uefi = True

    qemu = os.environ.get("QEMU")

    if not qemu:
        if not args.use_system_qemu and os.path.isfile(f"tools/host-qemu/bin/qemu-system-{args.arch}"):
            qemu = f"tools/host-qemu/bin/qemu-system-{args.arch}"
        else:
            qemu = f"qemu-system-{args.arch}"

    # Create a temporary directory that we use for various files.
    tmpdir = tempfile.TemporaryDirectory(prefix="vm-util-")

    # Determine if dmalog is available.

    have_dmalog = False

    devhelp = subprocess.check_output([qemu, "-device", "?"], encoding="ascii")
    for line in devhelp.splitlines():
        if line.startswith('name "dmalog"'):
            have_dmalog = True

    # Build the qemu command and run it.

    qemu_args = [
        "-s",
    ]

    if args.memory is not None:
        qemu_args += ["-m", args.memory]

    qemu_args += ["-name", f"Managarm {args.arch}"]
    if args.sdl:
        qemu_args += ["-display", "sdl"]
    else:
        qemu_args += ["-display", "gtk,zoom-to-fit=off"]

    have_kvm = False
    if not args.no_kvm:
        # Make sure we have KVM, and are going to run the same architecture
        if os.access("/dev/kvm", os.W_OK) and os.uname().machine == args.arch:
            qemu_args += ["-enable-kvm"]
            have_kvm = True
        else:
            print("No hardware virtualization available!", file=sys.stderr)

    if args.arch == "aarch64":
        # For aarch64 we use the virt machine
        qemu_args += ["-machine", "virt,acpi=off"]
        qemu_args += ["-serial", "stdio"]
        if not args.uefi:
            qemu_args += ["-kernel", "system-root/usr/managarm/bin/eir-linux.bin"]
            qemu_args += ["-initrd", "initrd.cpio"]
            qemu_args += ["-append", f"init.launch={args.init_launch}"]
    elif args.arch == "riscv64":
        # Use the virt machine and -kernel, similar to aarch64.
        qemu_args += ["-machine", "virt,acpi=off"]
        qemu_args += ["-serial", "stdio"]
        if not args.uefi:
            qemu_args += ["-kernel", "system-root/usr/managarm/bin/eir-linux.bin"]
            qemu_args += ["-initrd", "initrd.cpio"]
            qemu_args += ["-append", f"init.launch={args.init_launch}"]
    else:
        assert args.arch == "x86_64"
        qemu_args += ["-debugcon", "stdio"]
        qemu_args += ["-machine", "smbios-entry-point-type=64"]

    cpu_extras = []
    cpu_model = "host,migratable=no"

    if args.arch == "x86_64":
        if not have_kvm or args.virtual_cpu:
            cpu_model = "qemu64"
            cpu_extras = ["+smap", "+smep", "+umip", "+pcid", "+invpcid"]
        # Check for umip support, if the host does not support it, don't emulate it.
        with open("/proc/cpuinfo", 'r') as file:
            content = file.read()
            if not "umip" in content:
                cpu_extras = ["-umip"]
        if args.iommu:
            qemu_args += ["-device", "intel-iommu,intremap=on"]
            qemu_args += ["-M", "q35,kernel-irqchip=split"]
            qemu_args += ["-nodefaults"]
            if args.iommu_trace:
                qemu_args += ["--trace", "vtd*"]
    elif args.arch == "aarch64":
        if not have_kvm or args.virtual_cpu:
            cpu_model = "cortex-a72"
    else:
        assert args.arch == "riscv64"
        cpu_model = "rv64"
        cpu_extras = ["sv48=on", "svadu=on"]

    if cpu_extras:
        qemu_args += ["-cpu", cpu_model + "," + ",".join(cpu_extras)]
    else:
        qemu_args += ["-cpu", cpu_model]

    if not args.no_smp:
        qemu_args += ["-smp", "4"]

    if args.ci_script is not None:
        esp_uuid = None

        out = subprocess.check_output([which('sfdisk'), '-dJ', 'image'], encoding="ascii")
        for part in json.loads(out)['partitiontable']['partitions']:
            if part['type'].upper() == "C12A7328-F81F-11D2-BA4B-00A0C93EC93B":
                esp_uuid = part['uuid'].upper()
                break

        if not esp_uuid:
            print(f"error: no EFI System Partition found in image!")
            sys.exit(1)

        ci_config = os.path.join(tmpdir.name, "limine.conf")

        # Build the Limine config.
        ci_protocol = args.ci_protocol
        if ci_protocol is None:
            if args.uefi:
                ci_protocol = "uefi"
            elif args.arch == "x86_64":
                ci_protocol = "limine"
            else:
                assert args.arch in {"aarch64", "riscv64"}
                ci_protocol = "linux"
        with open(ci_config, "w") as f:
            f.write("limine:config:\n")
            f.write("timeout: 0\n")
            f.write("/ci-boot\n")
            if ci_protocol == "limine":
                f.write(f"kernel_path: guid({esp_uuid}):/managarm/eir-limine\n")
                f.write("protocol: limine\n")
            elif ci_protocol == "linux":
                f.write(f"kernel_path: guid({esp_uuid}):/managarm/eir-linux\n")
                f.write("protocol: linux\n")
            elif ci_protocol == "mb2":
                f.write(f"kernel_path: guid({esp_uuid}):/managarm/eir-mb2\n")
                f.write("protocol: multiboot2\n")
            elif ci_protocol == "uefi":
                f.write(f"image_path: guid({esp_uuid}):/managarm/eir-uefi\n")
                f.write("protocol: efi_chainload\n")
            else:
                raise RuntimeError(f"Bad --ci-protocol: {ci_protocol}")
            if ci_protocol in {"limine", "linux", "mb2"}:
                f.write(f"module_path: guid({esp_uuid}):/managarm/initrd.cpio\n")
            f.write("cmdline: bochs systemd.unit=ci-boot.target\n")

        qemu_args += [
            "-smbios",
            f"type=11,path={ci_config}",
        ]

    if args.uefi:
        # create a temporary OVMF_VARS.fd, as it likes to corrupt them, thus preventing boot, sigh
        tmp_ovmf_vars = tempfile.NamedTemporaryFile(suffix='.fd')
        shutil.copyfile(f"tools/ovmf/OVMF_VARS_{args.arch}.fd", tmp_ovmf_vars.name)

        qemu_args += ["-drive", f"if=pflash,format=raw,file=tools/ovmf/OVMF_CODE_{args.arch}.fd,readonly=on"]
        qemu_args += ["-drive", f"if=pflash,format=raw,file={tmp_ovmf_vars.name}"]
        if args.arch == "x86_64":
            qemu_args += ["-chardev", "file,id=uefi-load-base,path=uefi-load-base.addr"]
            qemu_args += ["-device", "isa-debugcon,iobase=0xCB7,chardev=uefi-load-base"]

    if args.ovmf_logs:
        if not args.uefi:
            print("OVMF logs without --uefi is useless")
            sys.exit(1)
        qemu_args += ["-chardev", "file,id=ovmf-logs,path=ovmf.log"]
        qemu_args += ["-device", "isa-debugcon,iobase=0x402,chardev=ovmf-logs"]

    # we have to handle this before other PCI devices, as we require this to be at 0000:00:02.0
    if args.gpu_passthrough and args.gpu_passthrough == "intel":
        gpu_memory_table = {
            32: 0x01,
            64: 0x02,
            96: 0x03,
            128: 0x04,
            160: 0x05,
            192: 0x06,
            224: 0x07,
            256: 0x08,
            288: 0x09,
            320: 0x0A,
            352: 0x0B,
            384: 0x0C,
            416: 0x0D,
            448: 0x0E,
            480: 0x0F,
            512: 0x10,
        }

        if args.gfx != "none":
            print("Intel GPU passthrough requires '--gfx none'")
            sys.exit(1)
        if args.intel_gpu_memory not in gpu_memory_table:
            print(f"{args.intel_gpu_memory} MiB memory is not a supported configuration for Intel Integrated GPUs")
            sys.exit(1)
        else:
            igd_gms = gpu_memory_table[args.intel_gpu_memory]
        with open("/sys/bus/pci/devices/0000:00:02.0/vendor") as f:
            if f.readline().strip() != "0x8086":
                print(f"No Intel integrated GPU available")
                sys.exit(1)
        with open("/sys/bus/pci/devices/0000:00:02.0/device") as f:
            devid = int(f.readline().strip()[2:], 16)

        igd_rom = None
        rom_mappings = {
            'SKL-1061': [0x1921, 0x1902, 0x1912, 0x1932, 0x1913, 0x1906, 0x1916, 0x1926, 0x1923, 0x1927, 0x193A, 0x190B, 0x191B, 0x192B, 0x193B, 0x190E, 0x191E, 0x191D, 0x192D, 0x193D, 0x5921, 0x5902, 0x5912, 0x5913, 0x5915, 0x5906, 0x5916, 0x5926, 0x5917, 0x590A, 0x591A, 0x590B, 0x591B, 0x593B, 0x591D, 0x590E, 0x591E, 0x5923, 0x5927, 0x5908],
        }

        for rom_name, ids in rom_mappings.items():
            if devid in ids:
                igd_rom = rom_name
                break
        if not igd_rom:
            print(f"No IGD ROM found for the GPU 8086:{devid:04x}")
            sys.exit(1)

        with open("/sys/bus/pci/devices/0000:00:02.0/class") as f:
            if not f.readline().strip().startswith("0x03"):
                print(f"No Intel integrated GPU available")
                sys.exit(1)
        if os.path.basename(os.readlink("/sys/bus/pci/devices/0000:00:02.0/driver")) != "vfio-pci":
            print(f"Intel integrated GPU not bound to vfio-pci")
            sys.exit(1)
        if not os.access("/sys/bus/pci/devices/0000:00:02.0/iommu_group", os.F_OK):
            print(f"Intel integrated GPU not bound to an IOMMU group")
            sys.exit(1)

        igd_rom_path = f"tools/igd-roms/{igd_rom}.rom"
        if not os.access(igd_rom_path, os.F_OK):
            print(f"IGD ROM file '{igd_rom_path}' is missing; please build the igd-roms tool!")
            sys.exit(1)

        qemu_args += ["-device", f"vfio-pci,host=00:02.0,x-igd-gms={igd_gms:#x},bus=pci.0,addr=2,x-igd-opregion=on,romfile={igd_rom_path},driver=vfio-pci-nohotplug"]

    # Add USB HCDs.
    if not args.inhibit_usb:
        qemu_args += [
            "-device",
            "piix3-usb-uhci,id=uhci",
            "-device",
            "usb-ehci,id=ehci",
            "-device",
            "qemu-xhci,id=xhci",
        ]

    # Add the boot medium.
    qemu_args += ["-drive", "id=boot-drive,file=image,format=raw,if=none"]

    if args.boot_drive == "virtio":
        qemu_args += ["-device", "virtio-blk-pci,drive=boot-drive"]
    elif args.boot_drive == "virtio-legacy":
        qemu_args += [
            "-device",
            "virtio-blk-pci,disable-modern=on,drive=boot-drive",
        ]
    elif args.boot_drive == "ahci":
        qemu_args += [
            "-device",
            "ahci,id=ahci",
            "-device",
            "ide-hd,drive=boot-drive,bus=ahci.0",
        ]
    elif args.boot_drive == "usb":
        # Use EHCI for now since XHCI hangs on boot.
        qemu_args += ["-device", "usb-storage,drive=boot-drive,bus=ehci.0"]
    elif args.boot_drive == "nvme":
        qemu_args += ["-device", "nvme,serial=deadbeef,drive=boot-drive"]
    elif args.boot_drive == "nvme-of":
        tftp_dir = setup_tftp_directory()
    elif args.boot_drive == "ide":
        qemu_args += ["-device", "ide-hd,drive=boot-drive,bus=ide.0"]
    else:
        assert args.boot_drive == "none"

    # Add networking.
    netdev_extra = ""
    if args.boot_drive == "nvme-of":
        netdev_extra += f",tftp={tftp_dir.name},bootfile="
        if args.uefi:
            arch = ""
            match args.arch:
                case "x86_64":
                    arch = "X64"
                case _:
                    print(f"error: unsupported arch '{args.arch}' for PXE")
                    sys.exit(1)
            netdev_extra += f"BOOT{arch}.EFI"
        else:
            netdev_extra += "limine-bios-pxe.bin"

    if args.net_bridge:
        qemu_args += ["-netdev", f"tap,id=net0{netdev_extra}"]
    elif args.nic != "none":
        qemu_args += ["-netdev", f"user,id=net0{netdev_extra}"]

    if args.nic == "i8254x":
        qemu_check_nic(qemu, qemu_args, "e1000")
        qemu_args += ["-device", "e1000,netdev=net0"]
    elif args.nic == "rtl8139":
        qemu_check_nic(qemu, qemu_args, "rtl8139")
        qemu_args += ["-device", "rtl8139,netdev=net0"]
    elif args.nic == "virtio":
        qemu_check_nic(qemu, qemu_args, "virtio-net-pci")
        qemu_args += ["-device", "virtio-net,disable-modern=on,netdev=net0"]
    elif args.nic == "usb":
        qemu_check_nic(qemu, qemu_args, "usb-net")
        qemu_args += ["-device", "usb-net,netdev=net0"]
    elif args.nic == "none":
        qemu_args += ["-net", "none"]

    if args.device_spec:
        spec = yaml.load(args.device_spec, Loader=yaml.SafeLoader)
        qemu_args += qemu_parse_device_spec(spec)

    if args.pci_passthrough:
        qemu_args += ["-device", f"vfio-pci,host={args.pci_passthrough}"]

    # Add graphics output.
    if args.gfx == "none":
        qemu_args += ["-vga", "none", "-display", "none"]
    elif args.gfx == "default":
        if args.arch == "x86_64":
            qemu_args += ["-vga", "virtio"]
        else:
            assert args.arch in {"aarch64", "riscv64"}
            qemu_args += ["-device", "virtio-gpu"]
    else:
        if args.arch == "x86_64":
            if args.gfx == "bga":
                qemu_args += ["-vga", "std"]
            else:  # virtio or vmware
                qemu_args += ["-vga", args.gfx]
        else:
            assert args.arch == "aarch64"
            if args.gfx == "bga":
                qemu_args += ["-device", "bochs-display"]
            elif args.gfx == "virtio":
                qemu_args += ["-device", "virtio-gpu"]
            else:
                assert args.gfx == "vmware"
                qemu_args += ["-device", "vmware-svga"]

    # Add HID devices.
    if not args.ps2:
        qemu_args += ["-device", "usb-kbd,bus=xhci.0"]
        if args.mouse:
            qemu_args += ["-device", "usb-mouse,bus=xhci.0"]
        else:
            qemu_args += ["-device", "usb-tablet,bus=xhci.0"]

    # Add debugging devices.
    if have_dmalog:
        qemu_args += [
            "-chardev",
            "file,id=ostrace,path=ostrace.bin",
            "-device",
            "dmalog,chardev=ostrace,tag=ostrace",
        ]

        qemu_args += [
            "-chardev",
            "file,id=kernel-profile,path=kernel-profile.bin",
            "-device",
            "dmalog,chardev=kernel-profile,tag=kernel-profile",
        ]

        qemu_args += [
            "-chardev",
            "file,id=kernel-alloc-trace,path=kernel-alloc-trace.bin",
            "-device",
            "dmalog,chardev=kernel-alloc-trace,tag=kernel-alloc-trace",
        ]

        if args.dmalog_int_pin == "none":
            dmalog_pin = "0"
        elif args.dmalog_int_pin.lower() in ['a', 'b', 'c', 'd']:
            dmalog_pin = ['a', 'b', 'c', 'd'].index(args.dmalog_int_pin.lower()) + 1
        else:
            print(f"Invalid dmalog interrupt pin '{args.dmalog_int_pin}'")
            sys.exit(1)

        qemu_args += [
            "-chardev",
            "socket,id=gdbsocket,host=0.0.0.0,port=5678,server=on,wait=no",
            "-device",
            f"dmalog,chardev=gdbsocket,tag=kernel-gdbserver,pin={dmalog_pin}",
        ]

    # Use serial for POSIX gdb (conflicts with headless init).
    if not args.ci_script is not None:
        qemu_args += [
            "-chardev",
            "socket,id=posix-gdbsocket,host=0.0.0.0,port=5679,server=on,wait=off",
            "-serial",
            "chardev:posix-gdbsocket",
        ]

    if args.usb_passthrough:
        for device in args.usb_passthrough:
            qemu_args += qemu_process_usb_passthrough(device, False)

    if args.usb_passthrough_pcap:
        for device in args.usb_passthrough_pcap:
            qemu_args += qemu_process_usb_passthrough(device, True)

    if args.usb_redir:
        qemu_check_device(qemu, qemu_args, 'usb-redir')

        for num, server in enumerate(args.usb_redir):
            [host, port] = server.rsplit(':', 1)
            qemu_args += ["-chardev", f"socket,id=usb-redir-chardev{num},port={port},host={host}"]
            qemu_args += ["-device", f"usb-redir,chardev=usb-redir-chardev{num},id=usb-redir{num},bus=xhci.0"]

    if args.usb_serial:
        qemu_args += ["-chardev", "file,path=serial.log,id=usb-serial"]
        qemu_args += ["-device", "usb-serial,chardev=usb-serial,bus=xhci.0"]

    if args.qmp:
        qemu_args += ["-qmp", "tcp:0.0.0.0:4444,server"]

    # TODO: Support virtio-console via:
    #       -chardev file,id=virtio-trace,path=virtio-trace.bin
    #       -device virtio-serial -device virtconsole,chardev=virtio-trace

    # Pass arguments from the enviornment.
    if "QFLAGS" in os.environ:
        qemu_args += shlex.split(os.environ["QFLAGS"])

    # Compile --expect and --expect-not into lists of regexp.
    expect_all = None
    if args.expect:
        expect_all = [re.compile(expr) for expr in args.expect]
    expect_none = []
    if args.expect_not:
        expect_none = [re.compile(expr) for expr in args.expect_not]

    # Add this last to not interfere with device probing.
    if args.ci_script is not None:
        qemu_args += [
            "-chardev",
            "socket,id=serial,server=on,wait=on,path=" + os.path.join(tmpdir.name, "serial.socket"),
            "-serial",
            "chardev:serial",
        ]

    with contextlib.ExitStack() as ctx_stack:
        logfile = None
        if args.logfile:
            logfile = ctx_stack.enter_context(open(args.logfile, "wb"))
        runner = QemuRunner(tmpdir=tmpdir.name, logfile=logfile, ci_script=args.ci_script, ci_downloads=args.ci_download)
        # Adjust for the fact that non-KVM runs are much slower.
        timeout_factor = 1 if have_kvm else 3
        if args.timeout is not None:
            runner.timeout = timeout_factor * args.timeout
        if args.io_timeout is not None:
            runner.io_timeout = timeout_factor * args.io_timeout
        asyncio.run(runner.run(qemu, qemu_args, expect_all=expect_all, expect_none=expect_none))


qemu_parser = main_subparsers.add_parser("qemu")
qemu_parser.set_defaults(_fn=do_qemu)
qemu_parser.add_argument("--arch", choices=["x86_64", "aarch64", "riscv64"], default="x86_64")
qemu_parser.add_argument("--memory", type=str, default="2G")
qemu_parser.add_argument("--no-kvm", action="store_true")
qemu_parser.add_argument("--virtual-cpu", action="store_true")
qemu_parser.add_argument("--no-smp", action="store_true")
qemu_parser.add_argument(
    "--boot-drive",
    choices=["virtio", "virtio-legacy", "ahci", "usb", "ide", "nvme", "nvme-of", "none"],
    default="virtio",
)
qemu_parser.add_argument("--net-bridge", action="store_true")
qemu_parser.add_argument("--nic", choices=["i8254x", "virtio", "rtl8139", "usb", "none"], default="virtio")
qemu_parser.add_argument("--gfx", choices=["bga", "virtio", "vmware", "none"], default="default")
qemu_parser.add_argument("--ps2", action="store_true")
qemu_parser.add_argument("--mouse", action="store_true")
qemu_parser.add_argument("--sdl", action="store_true")
qemu_parser.add_argument("--init-launch", type=str, default="weston")
qemu_parser.add_argument("--device-spec", type=argparse.FileType('r'))
qemu_parser.add_argument("--pci-passthrough", type=str)
qemu_parser.add_argument("--usb-passthrough", type=str, action='append')
qemu_parser.add_argument("--usb-passthrough-pcap", type=str, action='append')
qemu_parser.add_argument("--usb-redir", type=str, action='append')
qemu_parser.add_argument("--usb-serial", action='store_true')
qemu_parser.add_argument("--uefi", action=argparse.BooleanOptionalAction)
qemu_parser.add_argument("--ovmf-logs", action="store_true")
qemu_parser.add_argument("--dmalog-int-pin", type=str, default="C")
qemu_parser.add_argument("--ci-protocol", choices=["limine", "linux", "mb2", "uefi"])
qemu_parser.add_argument("--ci-script", type=str)
qemu_parser.add_argument("--ci-download", type=str, nargs="*", default=[])
qemu_parser.add_argument("--gpu-passthrough", choices=["intel", "none"], default="none")
qemu_parser.add_argument("--intel-gpu-memory", type=int, default="160")
qemu_parser.add_argument("--qmp", action="store_true")
qemu_parser.add_argument("--use-system-qemu", action="store_true")
qemu_parser.add_argument("--logfile", type=str)
qemu_parser.add_argument("--timeout", type=int)
qemu_parser.add_argument("--io-timeout", type=int)
qemu_parser.add_argument("--expect", action="append")
qemu_parser.add_argument("--expect-not", action="append")
qemu_parser.add_argument("--inhibit-usb", action="store_true")
qemu_parser.add_argument("--iommu", action="store_true")
qemu_parser.add_argument("--iommu-trace", action="store_true")

# ---------------------------------------------------------------------------------------
# gdb subcommand.
# ---------------------------------------------------------------------------------------


def do_gdb(args):
    gdb_args = ["gdb"]

    src_path = os.path.dirname(os.path.realpath("bootstrap.link"))
    gdb_args += ["-ex", f"source {src_path}/scripts/gdb-commands.py"]
    gdb_args += ["-ex", f"set substitute-path ../../../src {src_path}"]
    gdb_args += ["-ex", f"set substitute-path /var/lib/managarm-buildenv/ ../"]
    gdb_args += ["-ex", f"set sysroot system-root"]
    gdb_args += ["-ex", f"set debuginfod enabled off"]

    if args.gdb_debug:
        gdb_args += ["-ex", "set debug remote 1"]
        gdb_args += ["-ex", "set debug separate-debug-file 1"]

    if args.kernel:
        gdb_args += ["-ex", "python"]
        gdb_args += ["-ex", "import glob, os, sys"]
        gdb_args += ["-ex", "matches = glob.glob(\"system-root/usr/share/gcc*/python/\")"]
        gdb_args += ["-ex", "if matches:"]
        gdb_args += ["-ex", "\tsys.path.insert(0, matches[0])"]
        gdb_args += ["-ex", "\timport libstdcxx.v6.printers as libstdcxx_printers"]
        gdb_args += ["-ex", "\tlibstdcxx_printers.register_libstdcxx_printers(None)"]
        gdb_args += ["-ex", "end"]

    if args.qemu:
        if args.socket:
            remote_string = args.socket
        else:
            remote_string = "tcp:" + args.ip + ":1234"

        gdb_args += [
            "-ex",
            "file system-root/usr/managarm/bin/thor",
            "-ex",
            "target remote " + remote_string,
        ]
    elif args.uefi:
        try:
            import pefile
        except ImportError:
            print("error: please install the 'pefile' python module")
            sys.exit(1)

        if args.uefi_base:
            image_base = int(args.uefi_base, 16)
        else:
            with open("uefi-load-base.addr", mode="rb") as f:
                f.seek(0, os.SEEK_END)
                if f.tell() < 8:
                    print("error: no UEFI image base address found")
                    sys.exit(1)
                f.seek(-8, os.SEEK_END)
                image_base = struct.unpack("P", f.read())[0]

        eir_path_pe = "pkg-builds/managarm-kernel-uefi/kernel/eir/boot/uefi/eir-uefi"
        eir_path_debug = "pkg-builds/managarm-kernel-uefi/kernel/eir/boot/uefi/eir-uefi-elf"

        if not os.access(eir_path_debug, os.R_OK):
            eir_path_debug = eir_path_pe

        gdb_args += [
            "-ex", f"loadpe {image_base:#x} {eir_path_pe} {eir_path_debug}",
            "-ex", "target remote tcp:" + args.ip + ":1234",
            "-ex", "find-uefi-main"
        ]
    elif args.kernel:
        gdb_args += ["-ex", "target remote tcp:" + args.ip + ":5678"]
    else:
        assert args.posix
        gdb_args += [
            "-ex",
            "target remote tcp:" + args.ip + ":5679",
        ]

    os.execvp("gdb", gdb_args)


gdb_parser = main_subparsers.add_parser("gdb")
gdb_parser.set_defaults(_fn=do_gdb)
gdb_parser.add_argument("--ip", type=str, default="localhost")
gdb_parser.add_argument("--socket", type=str)
gdb_parser.add_argument("--gdb-debug", action='store_true')
gdb_parser.add_argument("--uefi-base", type=str)

gdb_group = gdb_parser.add_mutually_exclusive_group(required=True)
gdb_group.add_argument("--qemu", action="store_true")
gdb_group.add_argument("--uefi", action="store_true")
gdb_group.add_argument("--kernel", action="store_true")
gdb_group.add_argument("--posix", action="store_true")

# ---------------------------------------------------------------------------------------
# analyze-profile subcommand.
# ---------------------------------------------------------------------------------------


def do_profile(args):
    srcdir = os.path.dirname(os.readlink("bootstrap.link"))
    try:
        subprocess.check_call(
            [
                os.path.join(srcdir, "managarm/tools/analyze-profile.py"),
                "kernel-profile.bin",
            ]
        )
    except subprocess.CalledProcessError:
        sys.exit(1)


profile_parser = main_subparsers.add_parser("analyze-profile")
profile_parser.set_defaults(_fn=do_profile)

# ---------------------------------------------------------------------------------------
# analyze-alloc-trace subcommand.
# ---------------------------------------------------------------------------------------


def do_alloc_trace(args):
    try:
        subprocess.check_call(
            [
                "xbstrap",
                "runtool",
                "--",
                "ninja",
                "-C",
                "pkg-builds/frigg/",
                "slab_trace_analyzer",
            ]
        )
        subprocess.check_call(
            [
                "pkg-builds/frigg/slab_trace_analyzer",
                "kernel-alloc-trace.bin",
                "system-root/usr/managarm/bin/thor",
            ]
        )
    except subprocess.CalledProcessError:
        sys.exit(1)


alloc_trace_parser = main_subparsers.add_parser("alloc-trace")
alloc_trace_parser.set_defaults(_fn=do_alloc_trace)

# ---------------------------------------------------------------------------------------
# tftp subcommand.
# ---------------------------------------------------------------------------------------

def do_tftp(args):
    tftp_dir = setup_tftp_directory()
    if args.verbose:
        print(f"Temporary tftp root directory: {tftp_dir}")

    server = TftpServer(args)
    server.run(tftp_dir)

tftp_parser = main_subparsers.add_parser("tftp")
tftp_parser.add_argument("-v", "--verbose", action="store_true")
tftp_parser.set_defaults(_fn=do_tftp)

# ---------------------------------------------------------------------------------------
# wol subcommand.
# ---------------------------------------------------------------------------------------

def do_wol(args):
    def parse_mac(mac: str):
        sanitized_mac = mac.replace(':', '').replace('-', '').lower()

        if len(sanitized_mac) == 12:
            try:
                return bytes.fromhex(sanitized_mac)
            except ValueError as e:
                print(f"Error parsing MAC address: {e}")
                sys.exit(1)
        else:
            print(f"Error parsing MAC address")
            sys.exit(1)

    with open("wol.yml", "r") as f:
        yml = yaml.load(f, Loader=yaml.SafeLoader)

        if not args.interface:
            if "interface" in yml:
                args.interface = yml["interface"]
            else:
                print("No interface specified.")
                sys.exit(1)

        resolved_addr = None
        if len(args.target) == 17:
            mac_addr = args.target
        else:
            # parse aliases
            with open("wol.yml", "r") as f:
                if "alias" in yml and args.target in yml["alias"]:
                    resolved_addr = mac_addr = yml["alias"][args.target]
                else:
                    print(f"Could not resolve alias {args.target}")
                    sys.exit(1)

    mac_address_bytes = parse_mac(mac_addr)
    if len(mac_address_bytes) != 6:
        print(f"Invalid MAC address {args.target}")
        sys.exit(1)

    try:
        ifindex = socket.if_nametoindex(args.interface)
    except OSError as e:
        print(f"Interface '{args.interface}' not found: {e}")
        sys.exit(1)

    print(f"Waking {args.target}{f' ({resolved_addr})' if resolved_addr else ''} over interface '{args.interface}'")

    magic_packet = b'\xFF' * 6 + mac_address_bytes * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTOIFINDEX, ifindex)
    sock.sendto(magic_packet, ('<broadcast>', socket.getservbyname("discard")))
    sock.close()

wol_parser = main_subparsers.add_parser("wol")
wol_parser.add_argument("interface", nargs='?', type=str)
wol_parser.add_argument("target", type=str)
wol_parser.set_defaults(_fn=do_wol)

# ---------------------------------------------------------------------------------------
# vfio subcommand.
# ---------------------------------------------------------------------------------------

def do_vfio(args):
    sysfs_path = pathlib.Path(f"/sys/bus/pci/devices/{args.device}")
    if not sysfs_path.exists():
        print(f"Device {args.device} not found")
        sys.exit(1)

    if (sysfs_path / "driver").exists():
        with open(sysfs_path / "driver/unbind", "w") as f:
            f.write(args.device)

    with open(sysfs_path / "vendor", "r") as f: vendor = int(f.read().strip(), 16)
    with open(sysfs_path / "device", "r") as f: device = int(f.read().strip(), 16)

    try:
        with open("/sys/bus/pci/drivers/vfio-pci/new_id", "w") as f:
            f.write(f"{vendor:x} {device:x}")
    except FileExistsError:
        pass

    with open("/sys/bus/pci/drivers/vfio-pci/bind", "w") as f:
        f.write(args.device)

vfio_parser = main_subparsers.add_parser("vfio")
vfio_parser.add_argument("device", type=str)
vfio_parser.set_defaults(_fn=do_vfio)

# ---------------------------------------------------------------------------------------
# "main()" code.
# ---------------------------------------------------------------------------------------

args = main_parser.parse_args()
if "_fn" in args:
    args._fn(args)
else:
    main_parser.print_help()
