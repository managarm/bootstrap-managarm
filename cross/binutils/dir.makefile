
c := cross/binutils

$c_BARE_CONFIG := --prefix=$(TREEPATH)/host-installs/toolchain-bare
$c_BARE_CONFIG += --target=x86_64-elf --with-sysroot=$(TREEPATH)/sysroot-bare

.PHONY: all-$c
all-$c: $(TREEPATH)/$c/install-bare.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $(TREEPATH)/$c/*-bare.tag
	
$(TREEPATH)/$c/install-bare.tag: c := $c
$(TREEPATH)/$c/install-bare.tag: $(TREEPATH)/$c/configure-bare.tag
	cd $(TREEPATH)/$c/build-bare && make all-binutils all-gas all-ld \
			&& make install-binutils install-gas install-ld
	touch $@

$(TREEPATH)/$c/init-bare.tag: c := $c
$(TREEPATH)/$c/init-bare.tag:
	git submodule update --init $c/src
	touch $@

$(TREEPATH)/$c/configure-bare.tag: c := $c
$(TREEPATH)/$c/configure-bare.tag: $(TREEPATH)/$c/init-bare.tag
$(TREEPATH)/$c/configure-bare.tag: | $(TREEPATH)/host-installs/toolchain-bare
$(TREEPATH)/$c/configure-bare.tag: | $(TREEPATH)/sysroot-bare/usr/include
$(TREEPATH)/$c/configure-bare.tag: | $(TREEPATH)/sysroot-bare/usr/lib
	rm -rf $(TREEPATH)/$c/build-bare
	mkdir -p $(TREEPATH)/$c/build-bare
	cd $(TREEPATH)/$c/build-bare && ../src/configure $($c_BARE_CONFIG)
	touch $@

