
f := native-cairo
$f_up := cairo

$f_RUN := ACLOCAL_PATH=$B/prefixes/host-libtool/share/aclocal:$B/prefixes/host-pkg-config/share/aclocal
$f_RUN += $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.69 host-automake-v1.15 host-libtool
$f_RUN += host-protoc cross-binutils native-gcc
$f_RUN += --

# For now, we build without glesv2 backend as Weston prefers the image backend.
$f_CONFIGURE := $T/ports/$($f_up)/configure --host=x86_64-managarm --prefix=/usr
$f_CONFIGURE += --disable-maintainer-mode --with-sysroot=$B/system-root
$f_CONFIGURE_ENV := PKG_CONFIG=$B/prefixes/host-pkg-config/bin/pkg-config
$f_CONFIGURE_ENV += PKG_CONFIG_SYSROOT_DIR=$B/system-root
$f_CONFIGURE_ENV += PKG_CONFIG_PATH=$B/system-root/usr/lib/pkgconfig

$f_MAKE_ALL := make
$f_MAKE_INSTALL := make "DESTDIR=$B/system-root" install

$(call milestone_action,configure-$f install-$f)

configure-$f: | $(call upstream_tag,regenerate-$($f_up))
configure-$f:
	rm -rf $B/native/$f && mkdir -p $B/native/$f
	cd $B/native/$f && $($f_CONFIGURE_ENV) $($f_RUN) $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/native/$f && $($f_RUN) $($f_MAKE_ALL) && $($f_RUN) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,$@)

