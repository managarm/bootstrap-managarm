
f := cross-binutils
$f_up := binutils

$f_CONFIGURE := $T/ports/$($f_up)/configure --prefix=$B/prefixes/$f
$f_CONFIGURE += --target=x86_64-managarm --with-sysroot=$B/system-root

$f_MAKE_ALL := make all-binutils all-gas all-ld
$f_MAKE_INSTALL := make install-binutils install-gas install-ld

$f_KERNEL_TOOLS := for f in $B/prefixes/$f/bin/x86_64-managarm-*; do
$f_KERNEL_TOOLS += ln -sf $$(basename $$f) \
		"$B/prefixes/$f/bin/$$(basename $$f | sed 's/x86_64-managarm/x86_64-managarm-kernel/')";
$f_KERNEL_TOOLS += done

$(call milestone_action,configure-$f install-$f)

configure-$f: $(call upstream_tag,regenerate-$($f_up))
	rm -rf $B/host/$f && mkdir -p $B/host/$f
	cd $B/host/$f && $($f_CONFIGURE)
	touch $(call milestone_tag,$@)

install-$f: $(call milestone_tag,configure-$f)
	cd $B/host/$f && $($f_MAKE_ALL) && $($f_MAKE_INSTALL)
	# we use the same binutils for kernel + userspace.
	$($f_KERNEL_TOOLS)
	touch $(call milestone_tag,$@)

