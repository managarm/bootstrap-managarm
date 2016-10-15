
f := autoconf-v2.64

$f_ORIGIN = http://git.savannah.gnu.org/r/autoconf.git
$f_REF = v2.64

.PHONY: clone-$f init-$f
clone-$f: f := $f
init-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	git -C $T/ports/$f am $T/patches/$f/*.patch
	# the .tarball-version file lets us pretend that this is autoconf 2.64.
	# we do this so that other projects do not see something like 2.64.x-xxxx
	# that autoconf's build-aux/git-version-gen would produce otherwise.
	echo 2.64 > $T/ports/$f/.tarball-version
	cd $T/ports/$f && autoreconf -i
	touch $(call upstream_tag,init-$f)

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f
$(call upstream_tag,init-$f): f := $f
$(call upstream_tag,init-$f):
	make init-$f

