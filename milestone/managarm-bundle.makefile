
f := managarm-bundle
b := managarm
u := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg cross-gcc

$f_CONFIGURE := $T/$u/configure --sysroot=$B/sysroot
$f_CONFIGURE += --protoc=protoc --host-cxx=g++ --host-cppflags= --host-ldflags=
$f_CONFIGURE += --elf-cxx= --elf-as= --elf-ld=

.PHONY: configure-$f
configure-$f: f := $f
configure-$f: b := $b
configure-$f: u := $u

configure-$f: | $(call upstream_tag,clone-$u)
	rm -rf $B/$b && mkdir -p $B/$b
	cd $B/$b && $($f_CONFIGURE)
	touch $(call milestone_tag,configure-$f)

$(call milestone_tag,configure-$f): f := $f
$(call milestone_tag,configure-$f):
	make configure-$f

