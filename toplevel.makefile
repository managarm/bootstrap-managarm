
include $T/cross/autoconf-v2.64/dir.makefile
include $T/cross/binutils/dir.makefile
include $T/cross/gcc/dir.makefile
include $T/managarm/dir.makefile

DIRS := $B/cross/autoconf-v2.64 $B/cross/binutils $B/cross/gcc
DIRS += $B/managarm
DIRS += $B/host-install
DIRS += $B/host-install/x86_64-elf/sys-root/usr/include
DIRS += $B/host-install/x86_64-elf/sys-root/usr/lib

$(DIRS):
	mkdir -p $@

