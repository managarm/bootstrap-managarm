
f := native-libcofiber
$f_up := libcofiber

$f_RUN := $B/withprefix $B/prefixes cross-binutils native-gcc --

$f_MAKE_INSTALL := make -f $T/ports/$($f_up)/library.makefile S=$T/ports/$($f_up)
$f_MAKE_INSTALL += "DESTDIR=$B/system-root" prefix=/usr/
$f_MAKE_INSTALL += CXX=x86_64-managarm-g++ LD=x86_64-managarm-ld AS=x86_64-managarm-as
$f_MAKE_INSTALL += install

$(call milestone_action,install-$f)

install-$f: $(call upstream_tag,init-$($f_up))
	rm -rf $B/native/$f && mkdir -p $B/native/$f
	cd $B/native/$f && $($f_RUN) $($f_MAKE_INSTALL)
	touch $(call milestone_tag,$@)

