
c := cross/autoconf-v2.64

$c_ORIGIN = http://git.savannah.gnu.org/r/autoconf.git
$c_REF = v2.64

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
	git -C $c/repo checkout --detach $($c_REF) && git -C $c/repo clean -xf
	git -C $c/repo am $T/$c/*.patch
	# the .tarball-version file lets us pretend that this is autoconf 2.64.
	# we do this so that other projects do not see something like 2.64.x-xxxx
	# that autoconf's build-aux/git-version-gen would produce otherwise.
	cd $c/repo && echo 2.64 > .tarball-version
	cd $c/repo && autoreconf -i
	touch $@

$c/configure.tag: c := $c
$c/configure.tag: $c/init.tag
	rm -rf $c/build && mkdir -p $c/build
	cd $c/build && ../repo/configure --prefix=$(realpath .)/host-install
	touch $@
	
$c/install.tag: c := $c
$c/install.tag: $c/configure.tag
	cd $c/build && make && make install
	touch $@

