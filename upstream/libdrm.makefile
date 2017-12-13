
f := libdrm

$f_RUN := ACLOCAL_PATH=$B/prefixes/host-pkg-config/share/aclocal
$f_RUN += $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.69 host-automake-v1.11
$f_RUN += --

$f_ORIGIN = git://anongit.freedesktop.org/mesa/drm
$f_REF = libdrm-2.4.81

$(call upstream_action,clone-$f init-$f regenerate-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	git -C $T/ports/$f am $T/patches/$f/*.patch
	touch $(call upstream_tag,$@)

regenerate-$f: | $(call milestone_tag,install-host-autoconf-v2.69)
regenerate-$f: | $(call milestone_tag,install-host-automake-v1.11)
regenerate-$f: | $(call milestone_tag,install-host-libtool)
regenerate-$f: | $(call upstream_tag,init-$f)
	cd $T/ports/$f && NOCONFIGURE=yes $($f_RUN) ./autogen.sh
	touch $(call upstream_tag,$@)

