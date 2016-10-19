
f := binutils

$f_ORIGIN = git://sourceware.org/git/binutils-gdb.git
$f_REF = binutils-2_26

$f_RUNPKG := $s/runpkg $B/hostpkg cross-automake-v1.11
$f_RUNPKG += $s/runpkg $B/hostpkg cross-autoconf-v2.64

.PHONY: clone-$f init-$f regenerate-$f
clone-$f: f := $f
init-$f: f := $f
regenerate-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call milestone_tag,install-cross-autoconf-v2.64)
init-$f: | $(call milestone_tag,install-cross-automake-v1.11)
init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	git -C $T/ports/$f am $T/patches/$f/*.patch
	touch $(call upstream_tag,init-$f)

regenerate-$f: | $(call milestone_tag,install-cross-autoconf-v2.64)
regenerate-$f: | $(call milestone_tag,install-cross-automake-v1.11)
regenerate-$f: | $(call upstream_tag,init-$f)
	cd $T/ports/$f && cd ld && $($f_RUNPKG) autoreconf
	touch $(call upstream_tag,regenerate-$f)

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f
$(call upstream_tag,init-$f): f := $f
$(call upstream_tag,init-$f):
	make init-$f
$(call upstream_tag,regenerate-$f): f := $f
$(call upstream_tag,regenerate-$f):
	make regenerate-$f

