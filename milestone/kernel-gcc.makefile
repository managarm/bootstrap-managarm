
f := kernel-gcc
$f_up := gcc

$f_RUN := $B/withprefix $B/prefixes cross-binutils --

$f_CONFIGURE := $T/ports/$($f_up)/configure --prefix=$B/prefixes/$f
$f_CONFIGURE += --target=x86_64-managarm-kernel --with-sysroot=$B/kernel-root
$f_CONFIGURE += --enable-languages=c,c++
$f_CONFIGURE += --disable-shared --disable-hosted-libstdcxx

# set inhibit_libc to prevent libgcov build.
$f_MAKE_ALL := make all-gcc inhibit_libc=true
$f_MAKE_INSTALL := make install-gcc

$(call milestone_action,configure-$f install-$f)

configure-$f: | $(call milestone_tag,install-cross-binutils)
configure-$f: $(call upstream_tag,regenerate-$($f_up))
	rm -rf $B/host/$f && mkdir -p $B/host/$f
	cd $B/host/$f && $($f_RUN) $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: $(call milestone_tag,configure-$f)
	cd $B/host/$f && $($f_RUN) $($f_MAKE_ALL) && $($f_RUN) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,$@)

