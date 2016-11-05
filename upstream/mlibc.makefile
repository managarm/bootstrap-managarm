
f := mlibc

$f_ORIGIN = https://github.com/avdgrinten/mlibc.git
$f_REF = master

$(call upstream_action,clone-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

