#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
import sys

main_parser = argparse.ArgumentParser()
main_subparsers = main_parser.add_subparsers()

# ---------------------------------------------------------------------------------------
# qemu subcommand.
# ---------------------------------------------------------------------------------------

def do_qemu(args):
	qemu = os.environ.get('QEMU', f'qemu-system-{args.arch}')

	# Determine if dmalog is available.

	have_dmalog = False

	devhelp = subprocess.check_output([qemu] + ['-device', '?'], encoding='ascii')
	for line in devhelp.splitlines():
		if line.startswith('name "dmalog"'):
			have_dmalog = True

	# Build the qemu command and run it.

	qemu_args = [
		'-s',
		'-m', '2048',
	]

	have_kvm = False
	if not args.no_kvm:
		# Make sure we have KVM, and are going to run the same architecture
		if os.access('/dev/kvm', os.W_OK) and os.uname().machine == args.arch:
			qemu_args += ['-enable-kvm']
			have_kvm = True
		else:
			print('No hardware virtualization available!', file=sys.stderr)

	if args.arch == 'aarch64':
		# For aarch64 we use the virt machine
		qemu_args += ['-machine', 'virt']

		# For aarch64 we directly boot our kernel instead of using a bootloader
		# The following assumes we're in the build dir
		qemu_args += ['-kernel', 'pkg-builds/managarm-kernel/kernel/eir/arch/arm/virt/eir-virt.bin']
		qemu_args += ['-initrd', 'initrd.cpio']
		qemu_args += ['-append', f'init.launch={args.init_launch}']
		qemu_args += ['-serial', 'stdio']
	else:
		assert args.arch == 'x86_64'
		qemu_args += ['-debugcon', 'stdio']

	cpu_extras = [ ]
	cpu_model = 'host,migratable=no'

	if args.arch == 'x86_64':
		if not have_kvm or args.virtual_cpu:
			cpu_model = 'qemu64'
			cpu_extras = ['+smap', '+smep', '+umip', '+pcid', '+invpcid']
	else:
		assert args.arch == 'aarch64'
		if not have_kvm or args.virtual_cpu:
			cpu_model = 'cortex-a72'

	if cpu_extras:
		qemu_args += ['-cpu', cpu_model + ',' + ','.join(cpu_extras)]
	else:
		qemu_args += ['-cpu', cpu_model]

	if not args.no_smp:
		qemu_args += ['-smp', '4']

	# Add USB HCDs.
	qemu_args += [
		'-device', 'piix3-usb-uhci,id=uhci',
		'-device', 'usb-ehci,id=ehci',
		'-device', 'qemu-xhci,id=xhci'
	]

	# Add the boot medium.
	qemu_args += ['-drive', 'id=boot-drive,file=image,format=raw,if=none']

	if args.boot_drive == 'virtio':
		qemu_args += ['-device', 'virtio-blk-pci,drive=boot-drive']
	elif args.boot_drive == 'virtio-legacy':
		qemu_args += ['-device', 'virtio-blk-pci,disable-modern=on,drive=boot-drive']
	elif args.boot_drive == 'ahci':
		qemu_args += [
			'-device', 'ahci,id=ahci',
			'-device', 'ide-hd,drive=boot-drive,bus=ahci.0'
		]
	elif args.boot_drive == 'usb':
		# Use EHCI for now since XHCI hangs on boot.
		qemu_args += ['-device', 'usb-storage,drive=boot-drive,bus=ehci.0']
	else:
		assert args.boot_drive == 'ide'
		qemu_args += ['-device', 'ide-hd,drive=boot-drive,bus=ide.0']

	# Add networking.
	if args.net_bridge:
		qemu_args += ['-netdev', 'tap,id=net0']
	else:
		qemu_args += ['-netdev', 'user,id=net0']
	qemu_args += ['-device', 'virtio-net,disable-modern=on,netdev=net0']

	# Add graphics output.
	if args.gfx == 'default':
		if args.arch == 'x86_64':
			qemu_args += ['-vga', 'vmware']
		else:
			assert args.arch == 'aarch64'
			qemu_args += ['-device', 'virtio-gpu']
	else:
		if args.arch == 'x86_64':
			if args.gfx == 'bga':
				qemu_args += ['-vga', 'std']
			else: # virtio or vmware
				qemu_args += ['-vga', args.gfx]
		else:
			assert args.arch == 'aarch64'
			if args.gfx == 'bga':
				qemu_args += ['-device', 'bochs-display']
			elif args.gfx == 'virtio':
				qemu_args += ['-device', 'virtio-gpu']
			else:
				assert args.gfx == 'vmware'
				qemu_args += ['-device', 'vmware-svga']

	# Add HID devices.
	if not args.ps2:
		qemu_args += ['-device', 'usb-kbd,bus=xhci.0']
		if args.mouse:
			qemu_args += ['-device', 'usb-mouse,bus=xhci.0']
		else:
			qemu_args += ['-device', 'usb-tablet,bus=xhci.0']

	# Add debugging devices.
	if have_dmalog:
		qemu_args += [
			'-chardev', 'file,id=ostrace,path=ostrace.bin',
			'-device', 'dmalog,chardev=ostrace,tag=ostrace'
		]

		qemu_args += [
			'-chardev', 'file,id=kernel-profile,path=kernel-profile.bin',
			'-device', 'dmalog,chardev=kernel-profile,tag=kernel-profile'
		]

		qemu_args += [
			'-chardev', 'file,id=kernel-alloc-trace,path=kernel-alloc-trace.bin',
			'-device', 'dmalog,chardev=kernel-alloc-trace,tag=kernel-alloc-trace'
		]

		qemu_args += [
			'-chardev', 'socket,id=gdbsocket,host=0.0.0.0,port=5678,server=on,wait=no',
			'-device', 'dmalog,chardev=gdbsocket,tag=kernel-gdbserver'
		]

	# Use serial for POSIX gdb.
	qemu_args += [
		'-chardev', 'socket,id=posix-gdbsocket,host=0.0.0.0,port=5679,server=on,wait=off',
		'-serial', 'chardev:posix-gdbsocket'
	]

	# TODO: Add passthrough devices via:
	#       -device usb-host,vendorid=0x17ef,productid=0x602d

	# TODO: Support virtio-console via:
	#       -chardev file,id=virtio-trace,path=virtio-trace.bin
	#       -device virtio-serial -device virtconsole,chardev=virtio-trace

	# Pass arguments from the enviornment.
	if 'QFLAGS' in os.environ:
		qemu_args += shlex.split(os.environ['QFLAGS'])

	print('Running {} with flags {}'.format(qemu, qemu_args))
	try:
		subprocess.check_call([qemu] + qemu_args)
	except subprocess.CalledProcessError:
		sys.exit(1)

qemu_parser = main_subparsers.add_parser('qemu')
qemu_parser.set_defaults(_fn=do_qemu)
qemu_parser.add_argument('--arch',
	choices=['x86_64', 'aarch64'],
	default='x86_64')
qemu_parser.add_argument('--no-kvm', action='store_true')
qemu_parser.add_argument('--virtual-cpu', action='store_true')
qemu_parser.add_argument('--no-smp', action='store_true')
qemu_parser.add_argument('--boot-drive',
	choices=['virtio', 'virtio-legacy', 'ahci', 'usb', 'ide'],
	default='virtio')
qemu_parser.add_argument('--net-bridge', action='store_true')
qemu_parser.add_argument('--gfx',
	choices=['bga', 'virtio', 'vmware'],
	default='default')
qemu_parser.add_argument('--ps2', action='store_true')
qemu_parser.add_argument('--mouse', action='store_true')
qemu_parser.add_argument('--init-launch', type=str, default='weston')

# ---------------------------------------------------------------------------------------
# gdb subcommand.
# ---------------------------------------------------------------------------------------

def do_gdb(args):
	gdb_args = [ ]
	if args.qemu:
		gdb_args += [
			'--symbols=system-root/usr/managarm/bin/thor',
			'-ex', 'target remote tcp:localhost:1234'
		]
	elif args.kernel:
		gdb_args += [
			'-ex', 'target remote tcp:localhost:5678'
		]
	else:
		assert args.posix
		gdb_args += [
			'-ex', 'set sysroot system-root',
			'-ex', 'target remote tcp:localhost:5679'
		]

	try:
		subprocess.check_call(['gdb'] + gdb_args)
	except subprocess.CalledProcessError:
		sys.exit(1)

gdb_parser = main_subparsers.add_parser('gdb')
gdb_parser.set_defaults(_fn=do_gdb)

gdb_group = gdb_parser.add_mutually_exclusive_group(required=True)
gdb_group.add_argument('--qemu', action='store_true')
gdb_group.add_argument('--kernel', action='store_true')
gdb_group.add_argument('--posix', action='store_true')

# ---------------------------------------------------------------------------------------
# analyze-profile subcommand.
# ---------------------------------------------------------------------------------------

def do_profile(args):
	srcdir = os.path.dirname(os.readlink('bootstrap.link'))
	try:
		subprocess.check_call([
			os.path.join(srcdir, 'managarm/tools/analyze-profile.py'),
			'kernel-profile.bin'
		])
	except subprocess.CalledProcessError:
		sys.exit(1)

profile_parser = main_subparsers.add_parser('analyze-profile')
profile_parser.set_defaults(_fn=do_profile)

# ---------------------------------------------------------------------------------------
# analyze-alloc-trace subcommand.
# ---------------------------------------------------------------------------------------

def do_alloc_trace(args):
	try:
		subprocess.check_call([
			'xbstrap', 'runtool', '--',
			'ninja', '-C', 'pkg-builds/frigg/', 'slab_trace_analyzer'
		])
		subprocess.check_call([
			'pkg-builds/frigg/slab_trace_analyzer',
			'kernel-alloc-trace.bin',
			'system-root/usr/managarm/bin/thor'
		])
	except subprocess.CalledProcessError:
		sys.exit(1)

alloc_trace_parser = main_subparsers.add_parser('alloc-trace')
alloc_trace_parser.set_defaults(_fn=do_alloc_trace)

# ---------------------------------------------------------------------------------------
# "main()" code.
# ---------------------------------------------------------------------------------------

args = main_parser.parse_args()
if '_fn' in args:
	args._fn(args)
else:
	main_parser.print_help()
