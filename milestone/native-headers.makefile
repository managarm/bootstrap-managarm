
f := native-headers
$f_grp := mlibc

$(call milestone_action,install-$f)

install-$f: | $(call milestone_tag,configure-mlibc-bundle)
	mkdir -p $B/system-root/usr/include $B/system-root/usr/lib
	cd $B/$($f_grp) && make install-headers
	touch $(call milestone_tag,$@)

