
include $T/cross/autoconf-v2.64/dir.makefile
include $T/cross/automake-v1.11/dir.makefile
include $T/cross/libtool/dir.makefile
include $T/cross/binutils/dir.makefile
include $T/cross/gcc/dir.makefile
include $T/managarm/dir.makefile
include $T/mlibc/dir.makefile
include $T/cross/protobuf/dir.makefile

DIRS := cross/autoconf-v2.64 cross/automake-v1.11
DIRS += cross/binutils cross/gcc
DIRS += managarm
DIRS += mlibc
DIRS += host-install
DIRS += sysroot/usr/include
DIRS += sysroot/usr/lib

$(DIRS):
	mkdir -p $@

