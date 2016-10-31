
f := system-headers
$f_grp := mlibc

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,configure-mlibc-bundle)
	cd $B/$($f_grp) && make install-headers
	touch $(call milestone_tag,$@)

