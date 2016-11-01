
f := os-core
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils system-gcc
$f_RUN += --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-system-gcc)
install-$f: | $(call milestone_tag,install-os-libcofiber)
install-$f: | $(call milestone_tag,install-os-helix)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make gen-thor/user_boot gen-mbus
	cd $B/$($f_grp) && $($f_RUN) make all-thor/user_boot all-mbus
	cd $B/$($f_grp) && $($f_RUN) make install-thor/user_boot install-mbus
	touch $(call milestone_tag,$@)

