
f := rtdl
g := managarm
u := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11
$f_RUNPKG += $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg cross-gcc

$f_CONFIGURE := $T/$u/configure --sysroot=$B/sysroot
$f_CONFIGURE += --protoc=protoc --host-cxx=g++ --host-cppflags= --host-ldflags=
$f_CONFIGURE += --elf-cxx= --elf-as= --elf-ld=

.PHONY: configure-$f install-$f
configure-$f: f := $f
configure-$f: g := $g
configure-$f: u := $u
install-$f: f := $f
install-$f: g := $g
install-$f: u := $u

configure-$f: | $(call milestone_tag,install-cross-gcc)
configure-$f: | $(call upstream_tag,clone-$u)
	rm -rf $B/$g && mkdir -p $B/$g
	cd $B/$g && $($f_CONFIGURE)
	touch $(call milestone_tag,configure-$f)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/$g && $($f_RUNPKG) make gen-ld-init/linker
	cd $B/$g && $($f_RUNPKG) make all-ld-init/linker && $($f_RUNPKG) make install-ld-init/linker
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,configure-$f): f := $f
$(call milestone_tag,configure-$f):
	make configure-$f
$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

