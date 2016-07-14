
c := cross/gcc

.PHONY: all-$c
all-$c: $B/$c/install-native.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $B/$c/*-elf.tag

$B/$c/init.tag: c := $c
$B/$c/init.tag: | $B/$c
$B/$c/init.tag:
	cd $T && git submodule update --init $c/src
	cd $T/$c/src && git reset --hard && git clean -xf
	cd $T/$c/src && git am ../*.patch
	cd $T/$c/src && cd libstdc++-v3 && PATH=$B/host-install/bin:$$PATH autoconf
	cd $T/$c/src && ./contrib/download_prerequisites
	touch $@

# ---------------------------------------------------------
# build a freestanding toolchain
# ---------------------------------------------------------

# --without-headers makes sure that libgcc does not try to use system headers.
# unfortunately --without-headers cannot be combined with --with-sysroot.
$c_ELF_CONFIG := --prefix=$B/host-install
$c_ELF_CONFIG += --target=x86_64-elf --without-headers
$c_ELF_CONFIG += --enable-languages=c,c++

# note that we need the target binutils so that gcc configures properly
# gcc also complains if the /usr/include directory does not exist
$B/$c/configure-elf.tag: c := $c
$B/$c/configure-elf.tag: $B/$c/init.tag
$B/$c/configure-elf.tag: $B/cross/binutils/install-elf.tag
$B/$c/configure-elf.tag: | $B/host-install
	rm -rf $B/$c/build-elf
	mkdir -p $B/$c/build-elf
	cd $B/$c/build-elf && $T/$c/src/configure $($c_ELF_CONFIG)
	touch $@

$B/$c/install-elf.tag: c := $c
$B/$c/install-elf.tag: $B/$c/configure-elf.tag
	cd $B/$c/build-elf && make all-gcc && make install-gcc
	cd $B/$c/build-elf && make all-target-libgcc && make install-target-libgcc
	touch $@

# ---------------------------------------------------------
# build the native toolchain
# ---------------------------------------------------------

$c_NATIVE_CONFIG := --prefix=$B/host-install
$c_NATIVE_CONFIG += --target=x86_64-managarm --with-sysroot=$B/sysroot
$c_NATIVE_CONFIG += --enable-languages=c,c++

$B/$c/configure-native.tag: c := $c
$B/$c/configure-native.tag: $B/$c/init.tag
$B/$c/configure-native.tag: $B/cross/binutils/install-native.tag
$B/$c/configure-native.tag: | $B/host-install
	rm -rf $B/$c/build-native
	mkdir -p $B/$c/build-native
	cd $B/$c/build-native && $T/$c/src/configure $($c_NATIVE_CONFIG)
	touch $@

$B/$c/install-native.tag: c := $c
$B/$c/install-native.tag: $B/$c/configure-native.tag
$B/$c/install-native.tag: | $B/sysroot/usr/include
$B/$c/install-native.tag: | $B/sysroot/usr/lib
	cd $B/$c/build-native && make all-gcc && make install-gcc
	cd $B/$c/build-native && make all-target-libgcc && make install-target-libgcc
	touch $@

