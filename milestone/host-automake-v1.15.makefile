
f := host-automake-v1.15
$f_up := automake-v1.15
$f_RUN := $B/withprefix $B/prefixes host-autoconf-v2.69 --

$f_CONFIGURE := $T/ports/$($f_up)/configure --prefix=$B/prefixes/$f
$f_CONFIGURE += MAKEINFO=true

$(call milestone_action,configure-$f install-$f)

configure-$f: | $(call milestone_tag,install-host-autoconf-v2.69)
configure-$f: | $(call upstream_tag,regenerate-$($f_up))
	rm -rf $B/host/$f && mkdir -p $B/host/$f
	cd $B/host/$f && $($f_RUN) $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: $(call milestone_tag,configure-$f)
	cd $B/host/$f && $($f_RUN) make && $($f_RUN) make install
	# for some reason aclocal complains about this missing symlink but does not create it.
	#ln -s $B/prefixes/$f/share/aclocal-1.11 $B/prefixes/$f/share/aclocal
	touch $(call milestone_tag,$@)

