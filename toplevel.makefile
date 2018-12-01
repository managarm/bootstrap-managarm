
B = $(realpath .)
s = $T/scripts

upstream_tag = $T/tags/$1.tag
milestone_tag = tags/$1.tag

define _upstream_action =
.PHONY: $1
$1 $(call upstream_tag,$1): f := $f
$1: | $T/tags
$(call upstream_tag,$1):
	make $1

endef
upstream_action = $(eval $(foreach x,$1,$(call _upstream_action,$x)))

define _milestone_action =
.PHONY: $1
$1 $(call milestone_tag,$1): f := $f
$1: | $B/tags
$(call milestone_tag,$1):
	make $1

endef
milestone_action = $(eval $(foreach x,$1,$(call _milestone_action,$x)))

$T/tags $B/tags:
	mkdir -p $@

include $T/upstream/acpica.makefile
include $T/upstream/autoconf-v2.64.makefile
include $T/upstream/autoconf-v2.69.makefile
include $T/upstream/automake-v1.11.makefile
include $T/upstream/automake-v1.15.makefile
include $T/upstream/bash.makefile
include $T/upstream/binutils.makefile
include $T/upstream/boost.makefile
include $T/upstream/cairo.makefile
include $T/upstream/coreutils.makefile
include $T/upstream/cxxshim.makefile
include $T/upstream/eudev.makefile
include $T/upstream/frigg.makefile
include $T/upstream/gcc.makefile
include $T/upstream/kmscube.makefile
include $T/upstream/libasync.makefile
include $T/upstream/libcofiber.makefile
include $T/upstream/libdrm.makefile
include $T/upstream/libevdev.makefile
include $T/upstream/libexpat.makefile
include $T/upstream/libffi.makefile
include $T/upstream/libinput.makefile
include $T/upstream/libpng.makefile
include $T/upstream/libsmarter.makefile
include $T/upstream/libtool.makefile
include $T/upstream/libxkbcommon.makefile
include $T/upstream/managarm.makefile
include $T/upstream/mesa.makefile
include $T/upstream/mlibc.makefile
include $T/upstream/mtdev.makefile
include $T/upstream/nano.makefile
include $T/upstream/ncurses.makefile
include $T/upstream/pixman.makefile
include $T/upstream/pkg-config.makefile
include $T/upstream/protobuf.makefile
include $T/upstream/wayland.makefile
include $T/upstream/wayland-protocols.makefile
include $T/upstream/weston.makefile
include $T/upstream/xkeyboard-config.makefile
include $T/upstream/xorg-macros.makefile
include $T/upstream/zlib.makefile

include $T/milestone/cross-binutils.makefile
include $T/milestone/helpers.makefile
include $T/milestone/host-autoconf-v2.64.makefile
include $T/milestone/host-autoconf-v2.69.makefile
include $T/milestone/host-automake-v1.11.makefile
include $T/milestone/host-automake-v1.15.makefile
include $T/milestone/host-frigg_pb.makefile
include $T/milestone/host-libtool.makefile
include $T/milestone/host-pkg-config.makefile
include $T/milestone/host-protoc.makefile
include $T/milestone/host-xorg-macros.makefile
include $T/milestone/kernel-gcc.makefile
include $T/milestone/kernel-main.makefile
include $T/milestone/kernel-runtime.makefile
include $T/milestone/libarch.makefile
include $T/milestone/managarm-bundle.makefile
include $T/milestone/native-bash.makefile
include $T/milestone/native-boost.makefile
include $T/milestone/native-frigg.makefile
include $T/milestone/native-headers.makefile
include $T/milestone/native-helix.makefile
include $T/milestone/native-libasync.makefile
include $T/milestone/native-libcofiber.makefile
include $T/milestone/native-libsmarter.makefile
include $T/milestone/native-runtime.makefile
include $T/milestone/native-system.makefile
include $T/milestone/system-gcc.makefile

