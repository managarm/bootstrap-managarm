
f := ncurses

$f_RUN := $B/withprefix $B/prefixes
$f_RUN += host-autoconf-v2.69 host-automake-v1.15 host-libtool
$f_RUN += --

$f_ORIGIN = ftp://ftp.invisible-island.net/ncurses/ncurses.tar.gz

$(call upstream_action,clone-$f init-$f regenerate-$f)

clone-$f:
	cd $T/ports && wget $($f_ORIGIN)
	touch $(call upstream_tag,$@)

init-$f: | $(call upstream_tag,clone-$f)
	cd $T/ports && tar -xzf $f.tar.gz
	cd $T/ports && mv $f-6.1 ncurses
	cd $T/ports && rm $f.tar.gz
	touch $(call upstream_tag,$@)

regenerate-$f: | $(call milestone_tag,install-host-autoconf-v2.69)
regenerate-$f: | $(call milestone_tag,install-host-automake-v1.11)
regenerate-$f: | $(call upstream_tag,init-$f)
#	cd $T/ports/$f && $($f_RUN) ./autogen.sh
	touch $(call upstream_tag,$@)

