
f := host-autoconf-v2.69
u := autoconf-v2.69

.PHONY: configure-$f install-$f
configure-$f: f := $f
configure-$f: u := $u
install-$f: f := $f
install-$f: u := $u

configure-$f: | $(call upstream_tag,init-$u)
	rm -rf $B/host/$f && mkdir -p $B/host/$f
	cd $B/host/$f && $T/ports/$u/configure --prefix=$B/hostpkg/$f MAKEINFO=true
	touch $(call milestone_tag,configure-$f)

install-$f: | $(call milestone_tag,configure-$f)
	cd $B/host/$f && make && make install
	touch $(call milestone_tag,install-$f)

$(call milestone_tag,configure-$f): f := $f
$(call milestone_tag,configure-$f):
	make configure-$f
$(call milestone_tag,install-$f): f := $f
$(call milestone_tag,install-$f):
	make install-$f

