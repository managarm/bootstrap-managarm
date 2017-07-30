
f := native-drivers
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils native-gcc
$f_RUN += --

$(call milestone_action,install-$f)

$f_gen := gen-drivers/libblockfs gen-drivers/libevbackend \
	gen-drivers/gfx/bochs gen-drivers/gfx/intel gen-drivers/uart \
	gen-drivers/usb/hcds/uhci gen-drivers/usb/hcds/ehci \
	gen-drivers/usb/devices/hid gen-drivers/usb/devices/storage \
	gen-drivers/virtio
$f_all_libs := all-drivers/libblockfs all-drivers/libevbackend
$f_install_libs := install-drivers/libblockfs install-drivers/libevbackend
$f_all_progs := all-drivers/gfx/bochs all-drivers/gfx/intel all-drivers/uart \
	all-drivers/usb/hcds/uhci all-drivers/usb/hcds/ehci \
	all-drivers/usb/devices/hid all-drivers/usb/devices/storage \
	all-drivers/virtio
$f_install_progs := install-drivers/gfx/bochs install-drivers/gfx/intel install-drivers/uart \
	install-drivers/usb/hcds/uhci install-drivers/usb/hcds/ehci \
	install-drivers/usb/devices/hid install-drivers/usb/devices/storage \
	install-drivers/virtio

install-$f: | $(call milestone_tag,install-native-core)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make $($f_gen)
	cd $B/$($f_grp) && $($f_RUN) make $($f_all_libs)
	cd $B/$($f_grp) && $($f_RUN) make $($f_install_libs)
	cd $B/$($f_grp) && $($f_RUN) make $($f_all_progs)
	cd $B/$($f_grp) && $($f_RUN) make $($f_install_progs)
	touch $(call milestone_tag,$@)

