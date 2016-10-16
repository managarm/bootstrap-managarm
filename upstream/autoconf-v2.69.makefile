
f := autoconf-v2.69

$f_ORIGIN = http://git.savannah.gnu.org/r/autoconf.git
$f_REF = v2.69

.PHONY: clone-$f init-$f
clone-$f: f := $f
init-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	cd $T/ports/$f && autoreconf -i
	touch $(call upstream_tag,init-$f)

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f
$(call upstream_tag,init-$f): f := $f
$(call upstream_tag,init-$f):
	make init-$f

