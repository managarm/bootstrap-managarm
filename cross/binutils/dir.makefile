
c := cross/binutils

$c_ORIGIN = git://sourceware.org/git/binutils-gdb.git
$c_REF = binutils-2_26

.PHONY: all-$c
all-$c: $c/install-elf.tag $c/install-native.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $c/*-elf.tag

.PHONY: clone-$c
clone-$c: c := $c
clone-$c:
	$T/scripts/touch-if-fetch --no-shallow $c/clone.tag $c/repo $($c_ORIGIN) $($c_REF)

$c/clone.tag: clone-$c

.PHONY: init-$c
init-$c: c := $c
init-$c: | $c
init-$c: $c/clone.tag
	git -C $c/repo checkout --detach $($c_REF) && git -C $c/repo clean -xf
	git -C $c/repo apply $T/$c/managarm-target
	cd $c/repo && cd ld && PATH=$(realpath .)/host-install/bin:$$PATH autoreconf
	touch $c/init.tag

$c/init.tag: c := $c
$c/init.tag:
	$(MAKE) init-$c

# ---------------------------------------------------------
# build a freestanding toolchain
# ---------------------------------------------------------

$c_ELF_CONFIG := --prefix=$(realpath .)/host-install
$c_ELF_CONFIG += --target=x86_64-elf

$c/configure-elf.tag: c := $c
$c/configure-elf.tag: $c/init.tag
$c/configure-elf.tag: | host-install
	rm -rf $c/build-elf && mkdir -p $c/build-elf
	cd $c/build-elf && ../repo/configure $($c_ELF_CONFIG)
	touch $@

$c/install-elf.tag: c := $c
$c/install-elf.tag: $c/configure-elf.tag
	cd $c/build-elf && make all-binutils all-gas all-ld \
			&& make install-binutils install-gas install-ld
	touch $@

# ---------------------------------------------------------
# build the native toolchain
# ---------------------------------------------------------

$c_NATIVE_CONFIG := --prefix=$(realpath .)/host-install
$c_NATIVE_CONFIG += --target=x86_64-managarm --with-sysroot=$(realpath .)/sysroot

$c/configure-native.tag: c := $c
$c/configure-native.tag: $c/init.tag
$c/configure-native.tag: | host-install
	rm -rf $c/build-native && mkdir -p $c/build-native
	cd $c/build-native && ../repo/configure $($c_NATIVE_CONFIG)
	touch $@

install-$c-native: c := $c
install-$c-native: $c/configure-native.tag
	cd $c/build-native && make all-binutils all-gas all-ld \
			&& make install-binutils install-gas install-ld
	touch $c/install-native.tag

$c/install-native.tag: c := $c
$c/install-native.tag:
	$(MAKE) install-$c-native

