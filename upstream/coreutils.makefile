
f := coreutils

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.69 host-automake-v1.11
$f_RUN += --

$f_ORIGIN = git://git0.savannah.gnu.org/coreutils.git
$f_REF = v8.27

$(call upstream_action,clone-$f init-$f regenerate-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	touch $(call upstream_tag,$@)

regenerate-$f: | $(call milestone_tag,install-host-autoconf-v2.69)
regenerate-$f: | $(call milestone_tag,install-host-automake-v1.11)
#regenerate-$f: | $(call milestone_tag,install-host-libtool)
regenerate-$f: | $(call upstream_tag,init-$f)
	cd $T/ports/$f && $($f_RUN) ./bootstrap
	touch $(call upstream_tag,$@)

