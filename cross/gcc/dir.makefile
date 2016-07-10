
c := cross/gcc

# note that we specify --with-sysroot without an explicit path.
# this makes sure that gcc does not try to use any headers when building runtime libs.
$c_BARE_CONFIG := --prefix=$(TREEPATH)/host-installs/toolchain-bare
$c_BARE_CONFIG += --target=x86_64-elf --with-sysroot
$c_BARE_CONFIG += --enable-languages=c,c++

$c_PATH := $(TREEPATH)/host-installs/toolchain-bare/bin

.PHONY: all-$c
all-$c: $(TREEPATH)/$c/install-bare.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $(TREEPATH)/$c/*-bare.tag
	
$(TREEPATH)/$c/install-bare.tag: c := $c
$(TREEPATH)/$c/install-bare.tag: $(TREEPATH)/$c/configure-bare.tag
#	export PATH=$$PATH:$($c_PATH) &&
	cd $(TREEPATH)/$c/build-bare && make all-gcc && make install-gcc
	cd $(TREEPATH)/$c/build-bare && make all-target-libgcc && make install-target-libgcc
	touch $@

$(TREEPATH)/$c/init-bare.tag: c := $c
$(TREEPATH)/$c/init-bare.tag:
	git submodule update --init $c/src
	touch $@

# note that we need the target binutils so that gcc configures properly
# gcc also complains if the /usr/include directory does not exist
$(TREEPATH)/$c/configure-bare.tag: c := $c
$(TREEPATH)/$c/configure-bare.tag: $(TREEPATH)/$c/init-bare.tag
$(TREEPATH)/$c/configure-bare.tag: $(TREEPATH)/cross/binutils/install-bare.tag
$(TREEPATH)/$c/configure-bare.tag: | $(TREEPATH)/host-installs/toolchain-bare
$(TREEPATH)/$c/configure-bare.tag: | $(TREEPATH)/sysroot-bare/usr/include
$(TREEPATH)/$c/configure-bare.tag: | $(TREEPATH)/sysroot-bare/usr/lib
	rm -rf $(TREEPATH)/$c/build-bare
	mkdir -p $(TREEPATH)/$c/build-bare
#	export PATH=$$PATH:$($c_PATH) &&
	cd $(TREEPATH)/$c/build-bare && ../src/configure $($c_BARE_CONFIG)
	touch $@

