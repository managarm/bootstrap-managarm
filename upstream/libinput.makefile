
f := libinput

$f_RUN := ACLOCAL_PATH=$B/prefixes/host-pkg-config/share/aclocal
$f_RUN += $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.69 host-automake-v1.11
$f_RUN += --

$f_ORIGIN = https://github.com/wayland-project/libinput.git
$f_REF = 1.9.902

$(call upstream_action,clone-$f init-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
#	git -C $T/ports/$f am $T/patches/$f/*.patch
	touch $(call upstream_tag,$@)

