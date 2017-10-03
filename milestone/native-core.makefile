
f := native-core
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils native-gcc
$f_RUN += --

$(call milestone_action,install-$f)

$f_gen := gen-libarch gen-protocols/fs gen-protocols/hw \
	gen-protocols/mbus gen-protocols/usb \
	gen-mbus \
	gen-core/drm gen-core/virtio \
	gen-posix/subsystem gen-posix/init \
	install-thor/kernel-headers
$f_all_libs1 := all-libarch
$f_install_libs1 := install-libarch
$f_all_libs2 := all-protocols/fs all-protocols/hw \
	all-protocols/mbus all-protocols/usb
$f_install_libs2 := install-protocols/fs install-protocols/hw \
	install-protocols/mbus install-protocols/usb
$f_all_libs3 := all-core/drm all-core/virtio
$f_install_libs3 := install-core/drm install-core/virtio
$f_all_progs := all-mbus all-posix/subsystem all-posix/init
$f_install_progs := install-mbus install-posix/subsystem install-posix/init

install-$f: | $(call milestone_tag,install-native-gcc)
install-$f: | $(call milestone_tag,install-native-boost)
install-$f: | $(call milestone_tag,install-native-protobuf)
install-$f: | $(call milestone_tag,install-native-frigg)
install-$f: | $(call milestone_tag,install-native-libcofiber)
install-$f: | $(call milestone_tag,install-native-libasync)
install-$f: | $(call milestone_tag,install-native-helix)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make $($f_gen)
	cd $B/$($f_grp) && $($f_RUN) make $($f_all_libs1)
	cd $B/$($f_grp) && $($f_RUN) make $($f_install_libs1)
	cd $B/$($f_grp) && $($f_RUN) make $($f_all_libs2)
	cd $B/$($f_grp) && $($f_RUN) make $($f_install_libs2)
	cd $B/$($f_grp) && $($f_RUN) make $($f_all_libs3)
	cd $B/$($f_grp) && $($f_RUN) make $($f_install_libs3)
	cd $B/$($f_grp) && $($f_RUN) make $($f_all_progs)
	cd $B/$($f_grp) && $($f_RUN) make $($f_install_progs)
	touch $(call milestone_tag,$@)

