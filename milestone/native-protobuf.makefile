
f := native-protobuf
u := protobuf

$f_RUNPKG := $s/runpkg $B/hostpkg host-protoc
$f_RUNPKG += $s/runpkg $B/hostpkg cross-binutils
$f_RUNPKG += $s/runpkg $B/hostpkg system-gcc

$f_CONFIGURE := $T/ports/$u/configure --host=x86_64-managarm --prefix=/usr
$f_CONFIGURE += --with-protoc=protoc

$f_MAKE_ALL := make all
$f_MAKE_INSTALL := make "DESTDIR=$B/system-root" install

.PHONY: configure-$f install-$f
configure-$f: f := $f
configure-$f: u := $u
install-$f: f := $f
install-$f: u := $u

configure-$f: | $(call upstream_tag,init-$u)
	rm -rf $B/native/$f && mkdir -p $B/native/$f
	cd $B/native/$f && $($f_RUNPKG) $($f_CONFIGURE)
	touch $(call milestone_tag,configure-$f)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/native/$f && $($f_RUNPKG) $($f_MAKE_ALL) && $($f_RUNPKG) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,configure-$f): f := $f
$(call milestone_tag,configure-$f):
	make configure-$f
$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

