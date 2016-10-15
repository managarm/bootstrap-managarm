
f := cross-automake-v1.11
u := automake-v1.11

$f_RUNPKG := $s/runpkg $B/hostpkg cross-autoconf-v2.64

$f_CONFIGURE := $($f_RUNPKG) $T/ports/$u/configure --prefix=$B/hostpkg/$f \
		MAKEINFO=true

.PHONY: configure-$f install-$f
configure-$f: f := $f
configure-$f: u := $u
install-$f: f := $f
install-$f: u := $u

configure-$f: | $(call milestone_tag,install-cross-autoconf-v2.64)
configure-$f: | $(call upstream_tag,init-$u)
	rm -rf $B/cross/$f && mkdir -p $B/cross/$f
	cd $B/cross/$f && $($f_CONFIGURE)
	touch $(call milestone_tag,configure-$f)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/cross/$f && $($f_RUNPKG) make && $($f_RUNPKG) make install
	# for some reason aclocal complains about this missing symlink but does not create it.
	ln -s $B/hostpkg/$f/share/aclocal-1.11 $B/hostpkg/$f/share/aclocal
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,configure-$f): f := $f
$(call milestone_tag,configure-$f):
	make configure-$f
$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

