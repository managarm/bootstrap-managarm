
f := libtool

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.64 host-automake-v1.11
$f_RUN += --

$f_ORIGIN = http://git.savannah.gnu.org/r/libtool.git
$f_REF = v2.4.5

$(call upstream_action,clone-$f init-$f regenerate-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	git -C $T/ports/$f am $T/patches/$f/*.patch
	touch $(call upstream_tag,$@)

init-$f: | $(call milestone_tag,install-host-autoconf-v2.64)
init-$f: | $(call milestone_tag,install-host-automake-v1.11)
regenerate-$f: | $(call upstream_tag,init-$f)
	# libtool's ./bootstrap does a shallow clone with insufficient depth.
	cd $T/ports/$f && git submodule update gnulib
	cd $T/ports/$f && $($f_RUN) ./bootstrap
	touch $(call upstream_tag,$@)

