
f := os-kernel
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils kernel-gcc
$f_RUN += --

$f_MAKE_GEN := make gen-thor/kernel
$f_MAKE_ALL := make all-eir all-thor/kernel

$(call milestone_action,install-$f)

install-$f: | $(milestone_tag,install-kernel-gcc)
install-$f: | $(milestone_tag,install-host-frigg_pb)
install-$f: $(milestone_tag,configure-$($f_grp))
	cd $B/$($f_grp) && $($f_RUN) $($f_MAKE_GEN)
	cd $B/$($f_grp) && $($f_RUN) $($f_MAKE_ALL)
	touch $(call milestone_tag,$@)

