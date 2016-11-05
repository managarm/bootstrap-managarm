
f := libarch
b := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg kernel-gcc

$f_MAKE_INSTALL := make install-libarch

.PHONY: install-$f
install-$f: f := $f
install-$f: b := $b

install-$f:
	cd $B/$b && $($f_RUNPKG) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,$@)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

