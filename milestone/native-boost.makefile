
f := native-boost
u := boost

$f_RUNPKG := $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg system-gcc

.PHONY: install-$f
install-$f: f := $f
install-$f: u := $u

install-$f:
	cp -r --dereference $T/ports/$u/boost $B/system-root/usr/include
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

