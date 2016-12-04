
f := native-drivers
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils native-gcc
$f_RUN += --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-native-core)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make gen-drivers/uhci
	cd $B/$($f_grp) && $($f_RUN) make all-drivers/uhci
	cd $B/$($f_grp) && $($f_RUN) make install-drivers/uhci
	touch $(call milestone_tag,$@)

