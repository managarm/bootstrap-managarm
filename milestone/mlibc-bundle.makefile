
f := mlibc-bundle
$f_grp := mlibc
$f_up := mlibc

$f_CONFIGURE := $T/$($f_up)/configure --sysroot=$B/system-root
$f_CONFIGURE += --frigg-path=$T/managarm/frigg
$f_CONFIGURE += --managarm-src-path=$T/managarm
$f_CONFIGURE += --managarm-build-path=$B/managarm

$(call milestone_action,configure-$f)

configure-$f: | $(call upstream_tag,clone-$($f_up))
	rm -rf $B/$($f_grp) && mkdir -p $B/$($f_grp)
	cd $B/$($f_grp) && $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

