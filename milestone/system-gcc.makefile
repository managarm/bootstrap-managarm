
f := system-gcc
$f_up := gcc

$f_RUN := $B/withprefix $B/prefixes cross-binutils --

$f_CONFIGURE := $T/ports/$($f_up)/configure --prefix=$B/prefixes/$f
$f_CONFIGURE += --target=x86_64-managarm --with-sysroot=$B/system-root
$f_CONFIGURE += --enable-languages=c,c++ --disable-multilib

$f_MAKE_ALL := make all-gcc
$f_MAKE_INSTALL := make install-gcc

$(call milestone_action,configure-$f install-$f)

configure-$f: | $(call milestone_tag,install-cross-binutils)
configure-$f: | $(call milestone_tag,install-system-headers)
configure-$f: $(call upstream_tag,regenerate-$($f_up))
	rm -rf $B/host/$f && mkdir -p $B/host/$f
	cd $B/host/$f && $($f_RUN) $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: $(call milestone_tag,configure-$f)
	cd $B/host/$f && $($f_RUN) $($f_MAKE_ALL) && $($f_RUN) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,$@)

