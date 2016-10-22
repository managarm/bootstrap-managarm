
f := helpers

.PHONY: install-$f
install-$f: f := $f

# FIXME: configure managarm in a different way
install-$f:
	ln -s $T/scripts/mount $B/mount
	ln -s $T/scripts/umount $B/umount
	ln -s $T/scripts/mkimage $B/mkimage
	ln -s $T/scripts/run-qemu $B/run-qemu
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

