
c := cross/autoconf-v2.64

.PHONY: all-$c
all-$c: $B/$c/install.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $B/$c/*.tag

$B/$c/init.tag: c := $c
$B/$c/init.tag: | $B/$c
$B/$c/init.tag:
	cd $T && git submodule update --init $c/src
	cd $T/$c/src && git reset --hard && git clean -xf
	cd $T/$c/src && git am ../*.patch
	# the .tarball-version file lets us pretend that this is autoconf 2.64.
	# we do this so that other projects do not see something like 2.64.x-xxxx
	# that autoconf's build-aux/git-version-gen would produce otherwise.
	cd $T/$c/src && echo 2.64 > .tarball-version
	cd $T/$c/src && autoreconf -i
	touch $@

$B/$c/configure.tag: c := $c
$B/$c/configure.tag: $B/$c/init.tag
	rm -rf $B/$c/build
	mkdir -p $B/$c/build
	cd $B/$c/build && $T/$c/src/configure --prefix=$B/host-install
	touch $@
	
$B/$c/install.tag: c := $c
$B/$c/install.tag: $B/$c/configure.tag
	cd $B/$c/build && make && make install
	touch $@

