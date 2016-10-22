
f := libcofiber

$f_RUNPKG :=

$f_ORIGIN = https://github.com/avdgrinten/libcofiber.git
$f_REF = master

.PHONY: clone-$f init-$f
clone-$f: f := $f
init-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	touch $(call upstream_tag,init-$f)

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f
$(call upstream_tag,init-$f): f := $f
$(call upstream_tag,init-$f):
	make init-$f

