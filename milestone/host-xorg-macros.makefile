
f := host-xorg-macros
u := xorg-macros

# TODO: do we actually need those prefixes?
$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.64 host-automake-v1.11
$f_RUN += --

# We need to install xorg-macros into the automake prefix.
# Otherwise aclocal does not find xorg-macros's files.
$f_CONFIGURE := $T/ports/$u/configure --prefix=$B/prefixes/host-automake-v1.11

$(call milestone_action,configure-$f install-$f)

configure-$f: $(call upstream_tag,init-$u)
	rm -rf $B/host/$f && mkdir -p $B/host/$f
	cd $B/host/$f && $($f_RUN) $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: $(call milestone_tag,configure-$f)
	cd $B/host/$f && $($f_RUN) make all && $($f_RUN) make install
	touch $(call milestone_tag,$@)

