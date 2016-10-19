
f := kernel-libgcc
g := kernel-gcc
u := gcc

$f_RUNPKG := $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg kernel-gcc

$f_MAKE_ALL := make all-target-libgcc
$f_MAKE_INSTALL := make install-target-libgcc

.PHONY: install-$f
install-$f: f := $f
install-$f: g := $g
install-$f: u := $u

install-$f: | $(call milestone_tag,install-$g)
	cd $B/host/$g && $($f_RUNPKG) $($f_MAKE_ALL) && $($f_RUNPKG) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

