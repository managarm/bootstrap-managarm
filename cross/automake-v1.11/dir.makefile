
c := cross/automake-v1.11

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
	cd $T/$c/src && ./bootstrap
	touch $@

$B/$c/configure.tag: c := $c
$B/$c/configure.tag: $B/$c/init.tag
	rm -rf $B/$c/build
	mkdir -p $B/$c/build
	cd $B/$c/build && $T/$c/src/configure --prefix=$B/host-install \
		MAKEINFO=true AUTOCONF=$B/host-install/bin/autoconf AUTOM4TE=$B/host-install/bin/autom4te
	touch $@
	
$B/$c/install.tag: c := $c
$B/$c/install.tag: $B/$c/configure.tag
	cd $B/$c/build && make && make install
	touch $@

