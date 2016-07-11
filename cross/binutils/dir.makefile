
c := cross/binutils

$c_ELF_CONFIG := --prefix=$B/host-install
$c_ELF_CONFIG += --target=x86_64-elf --with-sysroot

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
	touch $@

$B/$c/configure-elf.tag: c := $c
$B/$c/configure-elf.tag: $B/$c/init-elf.tag
$B/$c/configure-elf.tag: | $B/host-install
$B/$c/configure-elf.tag: | $B/host-install/x86_64-elf/sys-root/usr/include
$B/$c/configure-elf.tag: | $B/host-install/x86_64-elf/sys-root/usr/lib
	rm -rf $B/$c/build-elf
	mkdir -p $B/$c/build-elf
	cd $B/$c/build-elf && $T/$c/src/configure $($c_ELF_CONFIG)
	touch $@

$B/$c/install-elf.tag: c := $c
$B/$c/install-elf.tag: $B/$c/configure-elf.tag
	cd $B/$c/build-elf && make all-binutils all-gas all-ld \
			&& make install-binutils install-gas install-ld
	touch $@

