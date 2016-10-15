

f := cross-binutils
u := binutils

$f_RUNPKG := $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11

$f_CONFIGURE := $($f_RUNPKG) $T/ports/$u/configure --prefix=$B/hostpkg/$f
$f_CONFIGURE += --target=x86_64-managarm --with-sysroot=$B/sysroot

$f_MAKE_ALL := $($f_RUNPKG) make all-binutils all-gas all-ld
$f_MAKE_INSTALL := $($f_RUNPKG) make install-binutils install-gas install-ld

.PHONY: configure-$f install-$f
configure-$f: f := $f
configure-$f: u := $u
install-$f: f := $f
install-$f: u := $u

configure-$f: | $(call upstream_tag,init-$u)
	rm -rf $B/cross/$f && mkdir -p $B/cross/$f
	cd $B/cross/$f && $($f_CONFIGURE)
	touch $(call milestone_tag,configure-$f)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/cross/$f && $($f_MAKE_ALL) && $($f_MAKE_INSTALL)
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,configure-$f): f := $f
$(call milestone_tag,configure-$f):
	make configure-$f
$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

