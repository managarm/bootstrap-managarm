
f := host-frigg_pb
b := managarm

$f_RUNPKG := $s/runpkg $B/hostpkg host-protoc

$f_MAKE_ALL := make all-tools/frigg_pb
$f_MAKE_INSTALL := make install-tools/frigg_pb

.PHONY: install-$f
install-$f: f := $f
install-$f: b := $b

install-$f:
	cd $B/$b && $($f_RUNPKG) $($f_MAKE_ALL) && $($f_RUNPKG) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

