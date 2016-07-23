
c := mlibc

.PHONY: all-$c
all-$c: $c/install-headers.tag $c/install.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $c/*.tag

$c_CONFIG := --sysroot=$(realpath .)/sysroot \
	--frigg-path=$(realpath $T/managarm/src/frigg) \
	--managarm-src-path=$(realpath $T/managarm/src) \
	--managarm-build-path=$(realpath managarm/build)

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

$c/install-headers.tag: c := $c
$c/install-headers.tag: $c/configure.tag
	cd $c/build && make install-headers
	touch $@

$c/install.tag: c := $c
$c/install.tag: $c/configure.tag
$c/install.tag: managarm/install-frigg.tag
$c/install.tag: managarm/install-rtdl.tag
	# TODO: gen should be done automatically by the mlibc makefile
	export PATH=$(realpath .)/host-install/bin:$$PATH \
		&& export LD_LIBRARY_PATH=$(realpath .)/host-install/lib \
		&& cd $c/build && make gen && make && make install
	touch $@

