
c := cross/gcc

$c_ORIGIN = git://gcc.gnu.org/git/gcc.git
$c_REF = gcc-6_1_0-release

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $c/*.tag

.PHONY: clone-$c
clone-$c: c := $c
clone-$c:
	$T/scripts/touch-if-fetch --no-shallow $c/clone.tag $c/repo $($c_ORIGIN) $($c_REF)

$c/clone.tag: clone-$c

$c/init.tag: c := $c
$c/init.tag: | $c
$c/init.tag: $c/clone.tag
	git -C $c/repo checkout --detach $($c_REF) \
		&& git -C $c/repo clean -xf -e{gmp,isl,mpc,mpfr}
	git -C $c/repo am $T/$c/*.patch
	cd $c/repo && ./contrib/download_prerequisites
	touch $@

$c/regenerate.tag: c := $c
$c/regenerate.tag: $c/init.tag
	cd $c/repo && cd libstdc++-v3 && PATH=$(realpath .)/host-install/bin:$$PATH autoconf
	touch $@

# ---------------------------------------------------------
# build a freestanding toolchain
# ---------------------------------------------------------

# --without-headers makes sure that libgcc does not try to use system headers.
# unfortunately --without-headers cannot be combined with --with-sysroot.
$c_ELF_CONFIG := --prefix=$(realpath .)/host-install
$c_ELF_CONFIG += --target=x86_64-elf --without-headers
$c_ELF_CONFIG += --enable-languages=c,c++

# note that we need the target binutils so that gcc configures properly
# gcc also complains if the /usr/include directory does not exist
$c/configure-elf.tag: c := $c
$c/configure-elf.tag: $c/regenerate.tag
$c/configure-elf.tag: cross/binutils/install-elf.tag
$c/configure-elf.tag: | host-install
	rm -rf $c/build-elf
	mkdir -p $c/build-elf
	cd $c/build-elf && ../repo/configure $($c_ELF_CONFIG)
	touch $@

$c/install-elf.tag: c := $c
$c/install-elf.tag: $c/configure-elf.tag
	cd $c/build-elf && make all-gcc && make install-gcc
	cd $c/build-elf && make all-target-libgcc && make install-target-libgcc
	touch $@

# ---------------------------------------------------------
# build the native toolchain
# ---------------------------------------------------------

$c_NATIVE_CONFIG := --prefix=$(realpath .)/host-install
$c_NATIVE_CONFIG += --target=x86_64-managarm --with-sysroot=$(realpath .)/sysroot
$c_NATIVE_CONFIG += --enable-languages=c,c++

$c/configure-native.tag: c := $c
$c/configure-native.tag: $c/regenerate.tag
$c/configure-native.tag: cross/binutils/install-native.tag
$c/configure-native.tag: | host-install
	rm -rf $c/build-native
	mkdir -p $c/build-native
	cd $c/build-native && ../repo/configure $($c_NATIVE_CONFIG)
	touch $@

$c/install-native-cxx.tag: c := $c
$c/install-native-cxx.tag: $c/configure-native.tag
$c/install-native-cxx.tag: | sysroot/usr/include
$c/install-native-cxx.tag: | sysroot/usr/lib
	cd $c/build-native && make all-gcc && make install-gcc
	touch $@

.PHONY: install-$c-native-libgcc
install-$c-native-libgcc: c := $c
install-$c-native-libgcc: $c/configure-native.tag
install-$c-native-libgcc: $c/install-native-cxx.tag
	cd $c/build-native && make all-target-libgcc && make install-target-libgcc
	touch $c/install-native-libgcc.tag

$c/install-native-libgcc.tag: install-$c-native-libgcc

.PHONY: install-$c-native-libstdcxx
install-$c-native-libstdcxx: c := $c
install-$c-native-libstdcxx: $c/configure-native.tag
install-$c-native-libstdcxx: $c/install-native-cxx.tag
	cd $c/build-native && make all-target-libstdc++-v3 && make install-target-libstdc++-v3
	touch $c/install-native-libstdcxx.tag

$c/install-native-libstdcxx.tag: install-$c-native-libstdcxx

