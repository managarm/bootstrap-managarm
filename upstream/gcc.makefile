
f := gcc

$f_RUNPKG := $s/runpkg $B/hostpkg cross-autoconf-v2.64
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11

$f_ORIGIN = git://gcc.gnu.org/git/gcc.git
$f_REF = gcc-6_1_0-release

.PHONY: clone-$f init-$f regenerate-$f
clone-$f: f := $f
init-$f: f := $f
regenerate-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf -e{gmp,isl,mpc,mpfr}
	git -C $T/ports/$f am $T/patches/$f/*.patch
	cd $T/ports/$f && ./contrib/download_prerequisites
	touch $(call upstream_tag,init-$f)

init-$f: | $(call milestone_tag,install-cross-autoconf-v2.64)
init-$f: | $(call milestone_tag,install-cross-automake-v1.11)
regenerate-$f: | $(call upstream_tag,init-$f)
	cd $T/ports/$f && cd libstdc++-v3 && $($f_RUNPKG) autoconf

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f
$(call upstream_tag,init-$f): f := $f
$(call upstream_tag,init-$f):
	make init-$f

