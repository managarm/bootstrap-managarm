
B = $(realpath .)
s = $T/scripts

upstream_tag = $T/tags/$1.tag
milestone_tag = tags/$1.tag

include $T/upstream/autoconf-v2.64.makefile
include $T/upstream/automake-v1.11.makefile
include $T/upstream/binutils.makefile
include $T/upstream/gcc.makefile

include $T/milestone/cross-autoconf-v2.64.makefile
include $T/milestone/cross-automake-v1.11.makefile
include $T/milestone/cross-binutils.makefile
include $T/milestone/cross-gcc.makefile

#include $T/cross/autoconf-v2.64/dir.makefile
#include $T/cross/automake-v1.11/dir.makefile
#include $T/cross/libtool/dir.makefile
#include $T/cross/binutils/dir.makefile
#include $T/cross/gcc/dir.makefile
#include $T/managarm/dir.makefile
#include $T/mlibc/dir.makefile
#include $T/cross/protobuf/dir.makefile

#DIRS := cross/autoconf-v2.64 cross/automake-v1.11
#DIRS += cross/binutils cross/gcc
#DIRS += managarm
#DIRS += mlibc
#DIRS += host-install
#DIRS += sysroot/usr/include
#DIRS += sysroot/usr/lib

#$(DIRS):
#	mkdir -p $@

