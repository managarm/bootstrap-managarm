
f := helix
b := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg system-gcc

.PHONY: install-$f
install-$f: f := $f
install-$f: b := $b

install-$f: | $(call milestone_tag,configure-managarm-bundle)
	cd $B/$b && $($f_RUNPKG) make all-hel && $($f_RUNPKG) make install-hel
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

