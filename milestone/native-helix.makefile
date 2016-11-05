
f := native-helix
$f_grp := managarm

$f_RUN := $B/withprefix $B/prefixes cross-binutils system-gcc --

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,configure-managarm-bundle)
	cd $B/$($f_grp) && $($f_RUN) make all-hel && $($f_RUN) make install-hel
	touch $(call milestone_tag,install-$f)

