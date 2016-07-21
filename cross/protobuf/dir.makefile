
c := cross/protobuf

$c_ORIGIN = https://github.com/google/protobuf.git
$c_REF = v3.0.0-beta-4

.PHONY: all-$c

all-$c: $c/configure-host.tag

.PHONY: clone-$c
clone-$c: c := $c
clone-$c:
	$T/scripts/touch-if-fetch $c/clone.tag $c/repo $($c_ORIGIN) $($c_REF)

$c/init.tag: c := $c
$c/init.tag: clone-$c
	git -C $c/repo checkout --detach $($c_REF)
	git -C $c/repo clean -xf
	cd $c/repo && export PATH=$(realpath .)/host-install/bin:$$PATH \
		&& ./autogen.sh

$c/init.tag: c := $c
$c/configure-host.tag: $c/init.tag
	rm -rf $c/build-host && mkdir -p $c/build-host
	cd $c/build-host

