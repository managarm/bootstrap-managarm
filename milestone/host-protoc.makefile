
f := host-protoc
$f_up := protobuf

$f_RUN_CONFIG := $B/withprefix $B/prefixes
$f_RUN_CONFIG += host-autoconf-v2.69 host-automake-v1.11
$f_RUN_CONFIG += --

$f_CONFIGURE := $T/ports/$($f_up)/configure --prefix=$B/prefixes/$f

$f_MAKE_ALL := make all
$f_MAKE_INSTALL := make install

$(call milestone_action,configure-$f install-$f)

configure-$f: | $(call milestone_tag,install-host-autoconf-v2.69)
configure-$f: | $(call milestone_tag,install-host-automake-v1.11)
configure-$f: $(call upstream_tag,regenerate-$($f_up))
	rm -rf $B/host/$f && mkdir -p $B/host/$f
	cd $B/host/$f && $($f_RUN_CONFIG) $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: $(call milestone_tag,configure-$f)
	cd $B/host/$f && $($f_MAKE_ALL) && $($f_MAKE_INSTALL)
	touch $(call milestone_tag,$@)

