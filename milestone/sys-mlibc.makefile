
f := sys-mlibc
g := mlibc

$f_RUNPKG := $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11
$f_RUNPKG += $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg cross-gcc

.PHONY: install-$f
install-$f: f := $f
install-$f: g := $g

install-$f: | $(call milestone_tag,install-sys-headers)
	cd $B/$g && $($f_RUNPKG) make gen
	cd $B/$g && $($f_RUNPKG) make
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

