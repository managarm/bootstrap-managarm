
f := libsupc++
g := cross-gcc
u := gcc

$f_RUNPKG := $s/runpkg $B/hostpkg cross-gcc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11

.PHONY: install-$f
install-$f: f := $f
install-$f: g := $g
install-$f: u := $u

install-$f: | $(call milestone_tag,install-$g)
	#cd $B/cross/$g && cd $($f_RUNPKG)
	#make all-target-libstdc++-v3
	#&& $($f_RUNPKG) install-
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

