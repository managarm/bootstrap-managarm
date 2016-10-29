
f := binutils
$f_ORIGIN := git://sourceware.org/git/binutils-gdb.git
$f_REF := binutils-2_26

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.64 host-automake-v1.11
$f_RUN += --

$(call upstream_action,clone-$f init-$f regenerate-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

init-$f: $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	git -C $T/ports/$f am $T/patches/$f/*.patch
	touch $(call upstream_tag,$@)

regenerate-$f: | $(call milestone_tag,install-host-autoconf-v2.64)
regenerate-$f: | $(call milestone_tag,install-host-automake-v1.11)
regenerate-$f: $(call upstream_tag,init-$f)
	cd $T/ports/$f && cd ld && $($f_RUN) autoreconf
	touch $(call upstream_tag,$@)

