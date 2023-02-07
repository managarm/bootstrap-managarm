#!/bin/sh
mlibc_path="$1"
kernel_header_path="$2"
shift 2
[ $# -eq 0 ] && set -- dripos lemon aero ironclad vinix lyre
cd pkg-builds/ || exit 1
for sysdep in "$@"; do
	if [ ! -d "mlibc-sysdep-$sysdep" ]; then
		meson setup \
			"-Dc_args=['-fno-stack-protector', '-U__linux__']" \
			"-Dcpp_args=['-fno-stack-protector', '-U__linux__']" \
			-Dbuild_tests=true \
			-Db_sanitize=undefined \
			"-Dlinux_kernel_headers=$kernel_header_path" \
			--cross-file "$mlibc_path"/ci/"$sysdep".cross-file mlibc-sysdep-"$sysdep" "$mlibc_path"
	fi
	ninja -C mlibc-sysdep-"$sysdep"
done
