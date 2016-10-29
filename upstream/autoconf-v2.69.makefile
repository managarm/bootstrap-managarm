
f := autoconf-v2.69
$f_URL := https://ftp.gnu.org/gnu/autoconf/autoconf-2.69.tar.xz

$(call upstream_action,download-$f)

download-$f:
	mkdir -p $T/ports/$f
	curl $($f_URL) | tar -xJC $T/ports/$f --transform 's/autoconf-2.69\///'
	touch $(call upstream_tag,$@)


