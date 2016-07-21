
c := cross/libtool

$c_ORIGIN = http://git.savannah.gnu.org/r/libtool.git
$c_REF = v2.4.5

.PHONY: all-$c
all-$c: $c/install.tag

.PHONY: clean-$c
clean-$c: c := $c
clean-$c:
	rm $c/*.tag

.PHONY: clone-$c
clone-$c: c := $c
clone-$c:
	$T/scripts/touch-if-fetch $c/clone.tag $c/repo $($c_ORIGIN) $($c_REF)

$c/clone.tag: clone-$c

$c/init.tag: c := $c
$c/init.tag: | $c
$c/init.tag: $c/clone.tag
	git -C $c/repo checkout --detach $($c_REF) -- && git -C $c/repo clean -xf
	cd $c/repo && ./bootstrap
	touch $@

$c/configure.tag: c := $c
$c/configure.tag: $c/init.tag
	rm -rf $c/build && mkdir -p $c/build
	export PATH=$(realpath .)/host-install/bin:$$PATH \
		&& cd $c/build && ../repo/configure --prefix=$(realpath .)/host-install
	touch $@
	
$c/install.tag: c := $c
$c/install.tag: $c/configure.tag
	cd $c/build && make && make install
	touch $@

