
f := host-libtool
u := libtool

# TODO: do we actually need those prefixes?
$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.64 host-automake-v1.11
$f_RUN += --

# We need to install libtool into the automake prefix.
# Otherwise aclocal does not find libtool's files.
$f_CONFIGURE := $T/ports/$u/configure --prefix=$B/prefixes/host-automake-v1.11

$(call milestone_action,configure-$f install-$f)

configure-$f: $(call upstream_tag,init-$u)
	rm -rf $B/cross/$f && mkdir -p $B/cross/$f
	cd $B/cross/$f && $($f_RUN) $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: $(call milestone_tag,configure-$f)
	cd $B/cross/$f && $($f_RUN) make all && $($f_RUN) make install
	touch $(call milestone_tag,$@)

