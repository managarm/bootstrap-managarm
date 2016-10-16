
f := protobuf

$f_RUNPKG := $s/runpkg $B/hostpkg host-autoconf-v2.69
$f_RUNPKG += $s/runpkg $B/hostpkg cross-automake-v1.11

$f_ORIGIN = https://github.com/google/protobuf.git
$f_REF = v3.1.0

.PHONY: clone-$f init-$f regenerate-$f
clone-$f: f := $f
init-$f: f := $f
regenerate-$f: f := $f

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,clone-$f)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f clean -xf
	touch $(call upstream_tag,init-$f)

regenerate-$f: | $(call milestone_tag,install-host-autoconf-v2.69)
regenerate-$f: | $(call milestone_tag,install-cross-automake-v1.11)
regenerate-$f: | $(call milestone_tag,install-cross-libtool)
regenerate-$f: | $(call upstream_tag,init-$f)
	cd $T/ports/$f && $($f_RUNPKG) ./autogen.sh
	touch $(call upstream_tag,regenerate-$f)

$(call upstream_tag,clone-$f): f := $f
$(call upstream_tag,clone-$f):
	make clone-$f
$(call upstream_tag,init-$f): f := $f
$(call upstream_tag,init-$f):
	make init-$f

