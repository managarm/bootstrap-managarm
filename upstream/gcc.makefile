
f := gcc
$f_ORIGIN := git://gcc.gnu.org/git/gcc.git
$f_REF := gcc-7_1_0-release

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.64 host-automake-v1.11
$f_RUN += --

$(call upstream_action,clone-$f init-$f regenerate-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

init-$f: $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf -e{gmp,isl,mpc,mpfr}
	git -C $T/ports/$f am $T/patches/$f/*.patch
	cd $T/ports/$f && ./contrib/download_prerequisites
	touch $(call upstream_tag,$@)

init-$f: | $(call milestone_tag,install-host-autoconf-v2.64)
init-$f: | $(call milestone_tag,install-host-automake-v1.11)
regenerate-$f: $(call upstream_tag,init-$f)
	cd $T/ports/$f && cd libstdc++-v3 && $($f_RUN) autoconf
	touch $(call upstream_tag,$@)

