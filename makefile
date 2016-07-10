
TREEPATH := $(shell pwd)

include cross/autoconf-v2.64/dir.makefile
include cross/binutils/dir.makefile
include cross/gcc/dir.makefile

DIRS := $(TREEPATH)/host-installs/toolchain-bare
DIRS += $(TREEPATH)/sysroot-bare/usr/include
DIRS += $(TREEPATH)/sysroot-bare/usr/lib

$(DIRS):
	mkdir -p $@

