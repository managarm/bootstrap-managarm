
f := automake-v1.11
$f_ORIGIN := http://git.savannah.gnu.org/r/automake.git
$f_REF := v1.11.6
$f_RUN := $B/withprefix $B/prefixes host-autoconf-v2.69 --

$(call upstream_action,clone-$f init-$f regenerate-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	git -C $T/ports/$f am $T/patches/$f/*.patch
	touch $(call upstream_tag,$@)

regenerate-$f: | $(call milestone_tag,install-helpers)
regenerate-$f: | $(call milestone_tag,install-host-autoconf-v2.69)
regenerate-$f: $(call upstream_tag,init-$f)
	cd $T/ports/$f && $($f_RUN) ./bootstrap
	touch $(call upstream_tag,$@)

