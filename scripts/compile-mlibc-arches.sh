#!/bin/sh
mlibc_path="$1"
kernel_header_path="$2"
shift 2
[ $# -eq 0 ] && set -- x86_64 aarch64 riscv64 x86

mkdir -p ci
cd ci || exit 1

for arch in "$@"; do
	mkdir -p "build-$arch"
	cat >"build-$arch/bootstrap-site.yml" <<EOF
define_options:
  arch: "$arch"
EOF
	ln -sf "$mlibc_path" src/mlibc
	ln -sf "$kernel_header_path" src/linux
	cp "$mlibc_path/ci/bootstrap.yml" "src/"
	cd "build-$arch" || exit 1
	xbstrap init ../src
	xbstrap install --rebuild mlibc
	meson test -C pkg-builds/mlibc -v
done
