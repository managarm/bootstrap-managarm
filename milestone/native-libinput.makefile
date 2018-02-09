
f := native-libinput
$f_up := libinput

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils native-gcc host-pkg-config
$f_RUN += --

$f_MESON := meson --cross-file $T/scripts/meson.cross-file
$f_MESON_ENV := PKG_CONFIG_SYSROOT_DIR=$B/system-root
$f_MESON_ENV += PKG_CONFIG_PATH=$B/system-root/usr/lib/pkgconfig

$f_MAKE_ALL := make all
$f_MAKE_INSTALL := make "DESTDIR=$B/system-root" install

$(call milestone_action,configure-$f install-$f)

configure-$f: | $(call upstream_tag,init-$($f_up))
configure-$f:
	rm -rf $B/native/$f && mkdir -p $B/native/$f
	$($f_MESON_ENV) $($f_RUN) $($f_MESON) $T/ports/$($f_up) $B/native/$f
	touch $(call milestone_tag,$@)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/native/$f && $($f_RUN) $($f_MAKE_ALL) && $($f_RUN) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,$@)

