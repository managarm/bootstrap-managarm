
f := libtool

$f_RUNPKG := $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11

$f_ORIGIN = http://git.savannah.gnu.org/r/libtool.git
$f_REF = v2.4.5

.PHONY: clone-$f init-$f regenerate-$f
clone-$f: f := $f
init-$f: f := $f
regenerate-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	touch $(call upstream_tag,init-$f)

init-$f: | $(call milestone_tag,install-cross-autoconf-v2.64)
init-$f: | $(call milestone_tag,install-cross-automake-v1.11)
regenerate-$f: | $(call upstream_tag,init-$f)
	# libtool's ./bootstrap does a shallow clone with insufficient depth.
	cd $T/ports/$f && git submodule update gnulib
	cd $T/ports/$f && $($f_RUNPKG) ./bootstrap
	touch $(call upstream_tag,regenerate-$f)

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f
$(call upstream_tag,init-$f): f := $f
$(call upstream_tag,init-$f):
	make init-$f

