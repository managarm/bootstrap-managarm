
f := os-boost
$f_up := boost

$(call milestone_action,install-$f)

install-$f:
	cp -r --dereference $T/ports/$($f_up)/boost $B/system-root/usr/include
	touch $(call milestone_tag,install-$f)

