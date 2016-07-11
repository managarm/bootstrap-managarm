
c := managarm

$c_CONFIG := --sysroot=$B/sysroot
# TODO: do not use the host protoc
$c_CONFIG += --protoc=protoc
$c_CONFIG += --elf-cxx=$B/host-install/bin/x86_64-elf-g++
$c_CONFIG += --elf-as=$B/host-install/bin/x86_64-elf-as
$c_CONFIG += --elf-ld=$B/host-install/bin/x86_64-elf-ld

.PHONY: all-$c
all-$c: $B/$c/install.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $B/$c/*.tag

$B/$c/init.tag: c := $c
$B/$c/init.tag: | $B/$c
$B/$c/init.tag:
	cd $T && git submodule update --init $c/src
	touch $@

$B/$c/configure.tag: c := $c
$B/$c/configure.tag: $B/$c/init.tag
	rm -rf $B/$c/build
	mkdir -p $B/$c/build
	cd $B/$c/build && $T/$c/src/configure $($c_CONFIG)
	touch $@

$B/$c/install.tag: c := $c
$B/$c/install.tag: $B/$c/configure.tag
	cd $B/$c/build && make all-thor/kernel
	touch $@

