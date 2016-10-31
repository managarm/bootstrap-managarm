
f := managarm-bundle
$f_grp := managarm
$f_up := managarm

$f_CONFIGURE := $T/$($f_up)/configure --sysroot=$B/system-root
$f_CONFIGURE += --protoc=protoc --host-cxx=g++
$f_CONFIGURE += --host-cppflags=-I$B/prefixes/host-protoc/include
$f_CONFIGURE += --host-ldflags=-L$B/prefixes/host-protoc/lib
$f_CONFIGURE += --elf-cxx= --elf-as= --elf-ld=

$(call milestone_action,configure-$f)

configure-$f: | $(call upstream_tag,clone-$($f_up))
	rm -rf $B/$($f_grp) && mkdir -p $B/$($f_grp)
	cd $B/$($f_grp) && $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

