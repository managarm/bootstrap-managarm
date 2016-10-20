
f := managarm-kernel
b := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg kernel-gcc

$f_MAKE_GEN := make gen-thor/kernel
$f_MAKE_ALL := make all-eir all-thor/kernel

.PHONY: install-$f
install-$f: f := $f
install-$f: b := $b

install-$f:
	cd $B/$b && $($f_RUNPKG) $($f_MAKE_GEN)
	cd $B/$b && $($f_RUNPKG) $($f_MAKE_ALL)
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

