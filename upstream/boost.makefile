
f := boost

$f_ORIGIN = https://github.com/boostorg/boost.git
$f_REF = boost-1.62.0

$(call upstream_action,clone-$f init-$f)

clone-$f:
	$T/scripts/fetch --no-shallow $T/ports/$f $($f_ORIGIN) $($f_REF)
	touch $(call upstream_tag,$@)

init-$f: | $(call upstream_tag,clone-$f)
	git -C $T/ports/$f checkout --detach $($f_REF)
	git -C $T/ports/$f submodule update --init
	git -C $T/ports/$f clean -xf
	touch $(call upstream_tag,$@)

