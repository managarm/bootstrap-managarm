
f := helpers

$(call milestone_action,install-$f)

install-$f:
	ln -sf $T/scripts/withprefix $B/withprefix
	ln -sf $T/scripts/mount $B/mount
	ln -sf $T/scripts/umount $B/umount
	ln -sf $T/scripts/mkimage $B/mkimage
	ln -sf $T/scripts/run-qemu $B/run-qemu
	touch $(call milestone_tag,$@)

