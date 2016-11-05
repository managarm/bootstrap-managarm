
f := native-rtdl
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils system-gcc
$f_RUN += --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-system-gcc)
install-$f: | $(call milestone_tag,install-host-frigg_pb)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make gen-ld-init/linker
	cd $B/$($f_grp) && $($f_RUN) make all-ld-init/linker && $($f_RUN) make install-ld-init/linker
	touch $(call milestone_tag,$@)

