
f := os-core
b := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg system-gcc

install-$f: f := $f
install-$f: b := $b

install-$f: | $(call milestone_tag,install-system-gcc)
install-$f: | $(call milestone_tag,configure-managarm-bundle)
	cd $B/$b && $($f_RUNPKG) make gen-thor/user_boot
	cd $B/$b && $($f_RUNPKG) make all-thor/user_boot
	cd $B/$b && $($f_RUNPKG) make install-thor/user_boot
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

