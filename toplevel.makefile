
B = $(realpath .)
s = $T/scripts

upstream_tag = $T/tags/$1.tag
milestone_tag = tags/$1.tag

include $T/upstream/autoconf-v2.64.makefile
include $T/upstream/autoconf-v2.69.makefile
include $T/upstream/automake-v1.11.makefile
include $T/upstream/libtool.makefile
include $T/upstream/protobuf.makefile
include $T/upstream/managarm.makefile
include $T/upstream/mlibc.makefile
include $T/upstream/binutils.makefile
include $T/upstream/gcc.makefile

# milestones that build host tools.
include $T/milestone/helpers.makefile
include $T/milestone/cross-autoconf-v2.64.makefile
include $T/milestone/host-autoconf-v2.69.makefile
include $T/milestone/cross-automake-v1.11.makefile
include $T/milestone/cross-libtool.makefile
include $T/milestone/host-protoc.makefile
include $T/milestone/host-frigg_pb.makefile
include $T/milestone/cross-binutils.makefile

# milestones that build the kernel toolchain and kernel.
include $T/milestone/kernel-gcc.makefile
include $T/milestone/kernel-libgcc.makefile
include $T/milestone/kernel-libstdc++.makefile
include $T/milestone/managarm-bundle.makefile
include $T/milestone/managarm-kernel.makefile

# milestones that build the system toolchain and actual system.
include $T/milestone/system-headers.makefile
include $T/milestone/system-gcc.makefile
include $T/milestone/system-rtdl.makefile
include $T/milestone/system-mlibc.makefile
include $T/milestone/system-libgcc.makefile
include $T/milestone/system-libstdc++.makefile

include $T/milestone/helix.makefile
include $T/milestone/libarch.makefile

include $T/milestone/native-protobuf.makefile

