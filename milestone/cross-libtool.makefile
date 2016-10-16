
f := cross-libtool
u := libtool

$f_RUNPKG += $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11

# We need to install libtool into the automake prefix.
# Otherwise aclocal does not find libtool's files.
$f_CONFIGURE := $($f_RUNPKG) $T/ports/$u/configure --prefix=$B/hostpkg/cross-automake-v1.11

$f_MAKE_ALL := $($f_RUNPKG) make all
$f_MAKE_INSTALL := $($f_RUNPKG) make install

.PHONY: configure-$f install-$f
configure-$f: f := $f
configure-$f: u := $u
install-$f: f := $f
install-$f: u := $u

configure-$f: | $(call milestone_tag,install-cross-binutils)
configure-$f: | $(call milestone_tag,install-sys-headers)
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

