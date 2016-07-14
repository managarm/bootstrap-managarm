
include $T/cross/autoconf-v2.64/dir.makefile
include $T/cross/automake-v1.11/dir.makefile
include $T/cross/binutils/dir.makefile
include $T/cross/gcc/dir.makefile
include $T/managarm/dir.makefile

DIRS := $B/cross/autoconf-v2.64 $B/cross/automake-v1.11
DIRS += $B/cross/binutils $B/cross/gcc
DIRS += $B/managarm
DIRS += $B/host-install
DIRS += $B/sysroot/usr/include
DIRS += $B/sysroot/usr/lib

$(DIRS):
	mkdir -p $@

