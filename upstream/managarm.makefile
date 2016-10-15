
f := managarm

$f_ORIGIN = https://github.com/avdgrinten/managarm.git
$f_REF = master

.PHONY: clone-$f
clone-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f

