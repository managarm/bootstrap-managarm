
f := native-libcofiber
u := libcofiber

$f_RUNPKG := $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg system-gcc

$f_MAKE_INSTALL := make -f $T/ports/$u/library.makefile S=$T/ports/$u
$f_MAKE_INSTALL += "DESTDIR=$B/system-root" prefix=/usr/
$f_MAKE_INSTALL += CXX=x86_64-managarm-g++ LD=x86_64-managarm-ld AS=x86_64-managarm-as
$f_MAKE_INSTALL += install

.PHONY: install-$f
install-$f: f := $f
install-$f: u := $u

install-$f: | $(call upstream_tag,init-$u)
	rm -rf $B/native/$f && mkdir -p $B/native/$f
	cd $B/native/$f && $($f_RUNPKG) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

