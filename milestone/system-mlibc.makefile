
f := system-mlibc
b := mlibc

$f_RUNPKG := $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg system-gcc

.PHONY: install-$f
install-$f: f := $f
install-$f: b := $b

install-$f: | $(call milestone_tag,install-system-headers)
	cd $B/$b && $($f_RUNPKG) make gen
	cd $B/$b && $($f_RUNPKG) make && $($f_RUNPKG) make install
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

