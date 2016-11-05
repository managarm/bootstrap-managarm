
f := acpica

$f_ORIGIN = https://github.com/acpica/acpica.git
$f_REF = R09_30_16

$(call upstream_action,clone-$f init-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
#	git -C $T/ports/$f am $T/patches/$f/*.patch
	touch $(call upstream_tag,$@)

