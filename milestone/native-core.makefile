
f := native-core
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils system-gcc
$f_RUN += --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-system-gcc)
install-$f: | $(call milestone_tag,install-native-boost)
install-$f: | $(call milestone_tag,install-native-protobuf)
install-$f: | $(call milestone_tag,install-native-libcofiber)
install-$f: | $(call milestone_tag,install-native-helix)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make gen-thor/user_boot
	cd $B/$($f_grp) && $($f_RUN) make all-thor/user_boot
	cd $B/$($f_grp) && $($f_RUN) make install-thor/user_boot
	cd $B/$($f_grp) && $($f_RUN) make gen-mbus
	cd $B/$($f_grp) && $($f_RUN) make all-mbus
	cd $B/$($f_grp) && $($f_RUN) make install-mbus
	cd $B/$($f_grp) && $($f_RUN) make gen-libmbus
	cd $B/$($f_grp) && $($f_RUN) make all-libmbus
	cd $B/$($f_grp) && $($f_RUN) make install-libmbus
	cd $B/$($f_grp) && $($f_RUN) make gen-protocols/fs
	cd $B/$($f_grp) && $($f_RUN) make all-protocols/fs
	cd $B/$($f_grp) && $($f_RUN) make install-protocols/fs
	# TODO: this should be replaced by a better protocol.
	cd $B/$($f_grp) && $($f_RUN) make install-thor/kernel-headers
	cd $B/$($f_grp) && $($f_RUN) make gen-thor/acpi
	cd $B/$($f_grp) && $($f_RUN) make all-thor/acpi
	cd $B/$($f_grp) && $($f_RUN) make install-thor/acpi
	cd $B/$($f_grp) && $($f_RUN) make gen-posix/subsystem
	cd $B/$($f_grp) && $($f_RUN) make all-posix/subsystem
	cd $B/$($f_grp) && $($f_RUN) make install-posix/subsystem
	cd $B/$($f_grp) && $($f_RUN) make gen-posix/init
	cd $B/$($f_grp) && $($f_RUN) make all-posix/init
	cd $B/$($f_grp) && $($f_RUN) make install-posix/init
	touch $(call milestone_tag,$@)

