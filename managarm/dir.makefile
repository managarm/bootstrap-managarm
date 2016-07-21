
c := managarm

$c_CONFIG := --sysroot=$(realpath .)/sysroot
# TODO: do not use the host protoc
$c_CONFIG += --protoc=protoc
$c_CONFIG += --elf-cxx=$(realpath .)/host-install/bin/x86_64-elf-g++
$c_CONFIG += --elf-as=$(realpath .)/host-install/bin/x86_64-elf-as
$c_CONFIG += --elf-ld=$(realpath .)/host-install/bin/x86_64-elf-ld

.PHONY: all-$c
all-$c: $c/install-thor.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $c/*.tag

$c/init.tag: c := $c
$c/init.tag: | $c
$c/init.tag:
	cd $T && git submodule update --init $c/src
	touch $@

$c/configure.tag: c := $c
$c/configure.tag: $c/init.tag
	rm -rf $c/build
	mkdir -p $c/build
	cd $c/build && $T/$c/src/configure $($c_CONFIG)
	touch $@

$c/install-thor.tag: c := $c
$c/install-thor.tag: $c/configure.tag
	cd $c/build && make all-thor/kernel
	touch $@

$c/install-frigg.tag: c := $c
$c/install-frigg.tag: $c/configure.tag
	cd $c/build && make install-frigg
	touch $@

