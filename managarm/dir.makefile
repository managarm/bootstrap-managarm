
c := managarm

$c_CONFIG := --sysroot=$(realpath .)/sysroot
# TODO: do not use the host protoc
$c_CONFIG += --protoc=protoc
$c_CONFIG += --host-cxx=g++
$c_CONFIG += --host-cppflags="-I $(realpath .)/host-install/include"
$c_CONFIG += --host-ldflags="-L $(realpath .)/host-install/lib"
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

.PHONY: build-$c-tools
build-$c-tools: c := $c
build-$c-tools: $c/configure.tag
	$T/scripts/touch-if-make $c/build-tools.tag $c/build all-tools/frigg_pb

$c/build-tools.tag: build-$c-tools

$c/install-thor.tag: c := $c
$c/install-thor.tag: $c/configure.tag
	cd $c/build && make all-thor/kernel
	touch $@

$c/install-frigg.tag: c := $c
$c/install-frigg.tag: $c/configure.tag
	cd $c/build && make install-frigg
	touch $@

$c/install-rtdl.tag: c := $c
$c/install-rtdl.tag: $c/configure.tag
	export LD_LIBRARY_PATH=$(realpath .)/host-install/lib \
	export PATH=$(realpath .)/host-install/bin:$$PATH \
		&& cd $c/build && make gen-ld-init/linker && \
		make all-ld-init/linker && make install-ld-init/linker
	touch $@

