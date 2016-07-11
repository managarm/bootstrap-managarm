
c := cross/gcc

# --without-headers makes sure that libgcc does not try to use system headers.
# unfortunately --without-headers cannot be combined with --with-sysroot.
$c_ELF_CONFIG := --prefix=$B/host-install
$c_ELF_CONFIG += --target=x86_64-elf --without-headers
$c_ELF_CONFIG += --enable-languages=c,c++

$c_PATH := $B/host-install/bin

.PHONY: all-$c
all-$c: $B/$c/install-elf.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $B/$c/*-elf.tag

$B/$c/init-elf.tag: c := $c
$B/$c/init-elf.tag: | $B/$c
$B/$c/init-elf.tag:
	cd $T && git submodule update --init $c/src
	cd $T/$c/src && ./contrib/download_prerequisites
	touch $@

# note that we need the target binutils so that gcc configures properly
# gcc also complains if the /usr/include directory does not exist
$B/$c/configure-elf.tag: c := $c
$B/$c/configure-elf.tag: $B/$c/init-elf.tag
$B/$c/configure-elf.tag: $B/cross/binutils/install-elf.tag
$B/$c/configure-elf.tag: | $B/host-install
$B/$c/configure-elf.tag: | $B/host-install/x86_64-elf/sys-root/usr/include
$B/$c/configure-elf.tag: | $B/host-install/x86_64-elf/sys-root/usr/lib
	rm -rf $B/$c/build-elf
	mkdir -p $B/$c/build-elf
#	export PATH=$$PATH:$($c_PATH) &&
	cd $B/$c/build-elf && $T/$c/src/configure $($c_ELF_CONFIG)
	touch $@

$B/$c/install-elf.tag: c := $c
$B/$c/install-elf.tag: $B/$c/configure-elf.tag
#	export PATH=$$PATH:$($c_PATH) &&
	cd $B/$c/build-elf && make all-gcc && make install-gcc
	cd $B/$c/build-elf && make all-target-libgcc && make install-target-libgcc
	touch $@

