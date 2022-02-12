#!/usr/bin/python3

import argparse
import os
import selectors
import signal
import subprocess
import sys
import time

timeout = 20 * 60
io_timeout = 30

parser = argparse.ArgumentParser()
parser.add_argument('--io-timeout', action='store_true')

args = parser.parse_args()

# Some boilerplate to get SIGCHLD notification (via a file descriptor).
(sig_poll_fd, sig_wake_fd) = os.pipe()
os.set_blocking(sig_poll_fd, False)
os.set_blocking(sig_wake_fd, False)
old_wake_fd = signal.set_wakeup_fd(sig_wake_fd, warn_on_full_buffer=False)
assert old_wake_fd == -1, 'Expected no wakeup FD to be present'

# Need to register a handler, otherwise set_wakeup_fd() will not trigger.
def noop_handler(signo, frame):
	pass

old_handler = signal.signal(signal.SIGCHLD, noop_handler)
assert not old_handler, 'Expected no SIGCHLD handler to be present'

# Setup file descriptors to communicate with qemu.
def try_unlink(path):
	try:
		os.unlink(path)
	except FileNotFoundError:
		pass

try_unlink('monitor.in')
try_unlink('monitor.out')
try_unlink('debugcon')

os.mkfifo('monitor.in')
os.mkfifo('monitor.out')
os.mkfifo('debugcon')

qemu_cmd = [
	'qemu-system-x86_64',
	'-snapshot',
	'-chardev', 'pipe,id=monitor-fifo,path=monitor',
	'-smp', '4',
	'-m', '1024',
	'-device', 'piix3-usb-uhci', '-device', 'usb-kbd', '-device', 'usb-tablet',
	'-drive', 'id=hdd,file=image,format=raw,if=none',
	'-device', 'virtio-blk-pci,drive=hdd',
	'-vga', 'virtio',
	'-display', 'none',
	'-debugcon', 'pipe:debugcon',
	'-monitor', 'chardev:monitor-fifo'
]

if os.access('/dev/kvm', os.W_OK):
	qemu_cmd.append('-enable-kvm')
else:
	timeout = 3 * timeout # 3x timeout to accommodate for tcg

# Start the qemu process.
proc = subprocess.Popen(qemu_cmd, stdin=subprocess.DEVNULL)

# Setup the main loop that waits for the process and/or I/O.
def open_pipe(path, mode):
	if mode == 'r':
		access = os.O_RDONLY
	else:
		assert mode == 'w'
		access = os.O_WRONLY
	fd = os.open(path, access) # We do not want O_TRUNC / O_CREAT!
	return os.fdopen(fd, mode + 'b', buffering=0)

monitor = open_pipe('monitor.in', 'w')
debugcon = open_pipe('debugcon', 'r')

sel = selectors.DefaultSelector()
sel.register(sig_poll_fd, selectors.EVENT_READ)
sel.register(debugcon.fileno(), selectors.EVENT_READ)
os.set_blocking(debugcon.fileno(), False)

proc_alive = True
debugcon_alive = True

buf = b''
sent_enter = False
logfile = open('test-image.log', 'wb')
success = False

start_time = time.time()
io_time = time.time()
while proc_alive or debugcon_alive:
	events = sel.select(1)
	for key, _ in events:
		if key.fd == sig_poll_fd:
			if proc.poll() is not None:
				proc_alive = False

			# Discard bytes from the wakeup FD.
			os.read(sig_poll_fd, 16)
		elif key.fd == debugcon.fileno():
			chunk = debugcon.read()
			# We must read non-zero bytes since select() returned readable.
			assert chunk is not None
			if len(chunk):
				sys.stdout.buffer.write(chunk)
				sys.stdout.buffer.flush()
				logfile.write(chunk)
				buf += chunk
			else:
				sel.unregister(debugcon.fileno())
				debugcon_alive = False

			io_time = time.time();

	# Send ENTER to select an entry from GRUB's boot menu.
	if not sent_enter and time.time() > start_time + 5:
		monitor.write(b'sendkey ret\n')
		sent_enter = True

	# Process data from Managarm.
	while True:
		head, sep, tail = buf.partition(b'\n')
		if not sep:
			break
		buf = tail

		# Look for a message that Weston prints after finishing boot.
		if head.endswith(b"launching '/usr/libexec/weston-desktop-shell'"):
			monitor.write(b'screendump after-boot.ppm\n')
			monitor.write(b'system_powerdown\n')
			success = True

	# Handle the timeout.
	if time.time() > start_time + timeout:
		proc.terminate()
	if args.io_timeout and time.time() > io_time + io_timeout:
		proc.terminate()

os.unlink('monitor.in')
os.unlink('monitor.out')
os.unlink('debugcon')

if not success:
	sys.exit(1)
