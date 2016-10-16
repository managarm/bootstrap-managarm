
f := helix
g := managarm
u := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg cross-gcc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11

.PHONY: install-$f
install-$f: f := $f
install-$f: g := $g
install-$f: u := $u

# FIXME: configure managarm in a different way
install-$f: | $(call milestone_tag,configure-rtdl)
	cd $B/$g && $($f_RUNPKG) make all-hel && $($f_RUNPKG) install-hel
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

