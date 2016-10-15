
f := sys-headers
g := mlibc
u := mlibc

$f_CONFIGURE := $T/$u/configure --sysroot=$B/sysroot
$f_CONFIGURE += --frigg-path=$T/managarm/frigg
$f_CONFIGURE += --managarm-src-path=$T/managarm
$f_CONFIGURE += --managarm-build-path=$B/managarm

.PHONY: configure-$f install-$f
configure-$f: f := $f
configure-$f: g := $g
configure-$f: u := $u
install-$f: f := $f
install-$f: g := $g
install-$f: u := $u

configure-$f: | $(call upstream_tag,clone-managarm)
configure-$f: | $(call upstream_tag,clone-$u)
	rm -rf $B/$g && mkdir -p $B/$g
	cd $B/$g && $($f_CONFIGURE)
	touch $(call milestone_tag,configure-$f)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/$g && make install-headers
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,configure-$f): f := $f
$(call milestone_tag,configure-$f):
	make configure-$f
$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

