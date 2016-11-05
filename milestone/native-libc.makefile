
f := native-libc
$f_grp := mlibc

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-protoc cross-binutils system-gcc
$f_RUN += --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-native-rtdl)
install-$f: $(call milestone_tag,configure-mlibc-bundle)
	cd $B/$($f_grp) && $($f_RUN) make gen
	cd $B/$($f_grp) && $($f_RUN) make && $($f_RUN) make install
	touch $(call milestone_tag,$@)

