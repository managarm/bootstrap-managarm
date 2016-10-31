
f := host-frigg_pb
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes host-protoc --

$f_MAKE_ALL := make all-tools/frigg_pb
$f_MAKE_INSTALL := make install-tools/frigg_pb

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,install-host-protoc)
install-$f: $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) $($f_MAKE_ALL) && $($f_RUN) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,install-$f)

