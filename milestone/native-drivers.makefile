
f := native-drivers
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils native-gcc
$f_RUN += --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-native-core)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make gen-drivers/libblockfs
	cd $B/$($f_grp) && $($f_RUN) make all-drivers/libblockfs
	cd $B/$($f_grp) && $($f_RUN) make install-drivers/libblockfs
	cd $B/$($f_grp) && $($f_RUN) make gen-drivers/libcompose
	cd $B/$($f_grp) && $($f_RUN) make all-drivers/libcompose
	cd $B/$($f_grp) && $($f_RUN) make install-drivers/libcompose
	cd $B/$($f_grp) && $($f_RUN) make gen-drivers/libterminal
	cd $B/$($f_grp) && $($f_RUN) make all-drivers/libterminal
	cd $B/$($f_grp) && $($f_RUN) make install-drivers/libterminal
	cd $B/$($f_grp) && $($f_RUN) make gen-drivers/virtio
	cd $B/$($f_grp) && $($f_RUN) make all-drivers/virtio
	cd $B/$($f_grp) && $($f_RUN) make install-drivers/virtio
	cd $B/$($f_grp) && $($f_RUN) make gen-drivers/vga_terminal
	cd $B/$($f_grp) && $($f_RUN) make all-drivers/vga_terminal
	cd $B/$($f_grp) && $($f_RUN) make install-drivers/vga_terminal
	cd $B/$($f_grp) && $($f_RUN) make gen-drivers/uhci
	cd $B/$($f_grp) && $($f_RUN) make all-drivers/uhci
	cd $B/$($f_grp) && $($f_RUN) make install-drivers/uhci
	touch $(call milestone_tag,$@)

