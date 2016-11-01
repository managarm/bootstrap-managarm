
f := kernel-runtime
$f_grp := kernel-gcc

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += cross-binutils kernel-gcc
$f_RUN += --

$f_MAKE_ALL_LIBGCC := make all-target-libgcc
$f_MAKE_INSTALL_LIBGCC := make install-target-libgcc

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-kernel-gcc)
	mkdir -p $B/kernel-root/usr/include
	cp $T/patches/kernel-libc/* $B/kernel-root/usr/include
	cd $B/host/$($f_grp) && $($f_RUN) make all-target-libgcc
	cd $B/host/$($f_grp) && $($f_RUN) make install-target-libgcc
	cd $B/host/$($f_grp) && $($f_RUN) make all-target-libstdc++-v3
	cd $B/host/$($f_grp) && $($f_RUN) make install-target-libstdc++-v3
	touch $(call milestone_tag,install-$f)

