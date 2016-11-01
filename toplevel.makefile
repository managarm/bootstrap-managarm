
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

include $T/upstream/autoconf-v2.64.makefile
include $T/upstream/autoconf-v2.69.makefile
include $T/upstream/automake-v1.11.makefile
include $T/upstream/binutils.makefile
include $T/upstream/boost.makefile
include $T/upstream/gcc.makefile
include $T/upstream/libcofiber.makefile
include $T/upstream/libtool.makefile
include $T/upstream/managarm.makefile
include $T/upstream/mlibc.makefile
include $T/upstream/protobuf.makefile

include $T/milestone/cross-binutils.makefile
include $T/milestone/cross-libtool.makefile
include $T/milestone/helix.makefile
include $T/milestone/helpers.makefile
include $T/milestone/host-autoconf-v2.64.makefile
include $T/milestone/host-autoconf-v2.69.makefile
include $T/milestone/host-automake-v1.11.makefile
include $T/milestone/host-frigg_pb.makefile
include $T/milestone/host-protoc.makefile
include $T/milestone/kernel-gcc.makefile
include $T/milestone/kernel-libgcc.makefile
include $T/milestone/kernel-libstdc++.makefile
include $T/milestone/libarch.makefile
include $T/milestone/managarm-bundle.makefile
include $T/milestone/mlibc-bundle.makefile
include $T/milestone/native-boost.makefile
include $T/milestone/native-protobuf.makefile
include $T/milestone/native-libcofiber.makefile
include $T/milestone/os-core.makefile
include $T/milestone/os-kernel.makefile
include $T/milestone/system-gcc.makefile
include $T/milestone/system-headers.makefile
include $T/milestone/system-libc.makefile
include $T/milestone/system-rtdl.makefile
include $T/milestone/system-runtime.makefile

