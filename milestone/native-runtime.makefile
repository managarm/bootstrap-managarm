
f := native-runtime
$f_grp := system-gcc

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += cross-binutils system-gcc
$f_RUN += --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-native-libc)
install-$f: $(call milestone_tag,configure-$($f_grp))
	cd $B/host/$($f_grp) && $($f_RUN) make all-target-libgcc
	cd $B/host/$($f_grp) && $($f_RUN) make install-target-libgcc
	cd $B/host/$($f_grp) && $($f_RUN) make all-target-libstdc++-v3
	cd $B/host/$($f_grp) && $($f_RUN) make install-target-libstdc++-v3
	touch $(call milestone_tag,$@)

