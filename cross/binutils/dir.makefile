
c := cross/binutils

.PHONY: all-$c
all-$c: $B/$c/install-elf.tag $B/$c/install-native.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $B/$c/*-elf.tag

.PHONY: init-$c
init-$c: c := $c
init-$c: | $B/$c
init-$c:
	cd $T && git submodule update --init $c/src
	cd $T/$c/src && git reset --hard && git clean -xf
	cd $T/$c/src && git apply ../managarm-target
	cd $T/$c/src && cd ld && PATH=$B/host-install/bin:$$PATH autoreconf
	touch $B/$c/init.tag

$B/$c/init.tag: c := $c
$B/$c/init.tag:
	$(MAKE) init-$c

# ---------------------------------------------------------
# build a freestanding toolchain
# ---------------------------------------------------------

$c_ELF_CONFIG := --prefix=$B/host-install
$c_ELF_CONFIG += --target=x86_64-elf

$B/$c/configure-elf.tag: c := $c
$B/$c/configure-elf.tag: $B/$c/init.tag
$B/$c/configure-elf.tag: | $B/host-install
	rm -rf $B/$c/build-elf
	mkdir -p $B/$c/build-elf
	cd $B/$c/build-elf && $T/$c/src/configure $($c_ELF_CONFIG)
	touch $@

$B/$c/install-elf.tag: c := $c
$B/$c/install-elf.tag: $B/$c/configure-elf.tag
	cd $B/$c/build-elf && make all-binutils all-gas all-ld \
			&& make install-binutils install-gas install-ld
	touch $@

# ---------------------------------------------------------
# build the native toolchain
# ---------------------------------------------------------

$c_NATIVE_CONFIG := --prefix=$B/host-install
$c_NATIVE_CONFIG += --target=x86_64-managarm --with-sysroot=$B/sysroot

$B/$c/configure-native.tag: c := $c
$B/$c/configure-native.tag: $B/$c/init.tag
$B/$c/configure-native.tag: | $B/host-install
	rm -rf $B/$c/build-native
	mkdir -p $B/$c/build-native
	cd $B/$c/build-native && $T/$c/src/configure $($c_NATIVE_CONFIG)
	touch $@

install-$c-native: c := $c
install-$c-native: $B/$c/configure-native.tag
	cd $B/$c/build-native && make all-binutils all-gas all-ld \
			&& make install-binutils install-gas install-ld
	touch $B/$c/install-native.tag

$B/$c/install-native.tag: c := $c
$B/$c/install-native.tag:
	$(MAKE) install-$c-native

