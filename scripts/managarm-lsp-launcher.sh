#!/bin/sh

# parse options
XBSTRAP="xbstrap"
BUILD_DIR=""
while [ $# -gt 0 ]; do
    case "$1" in
        --xbstrap-bin=*)
            XBSTRAP="${1#*=}"
            shift 1
            ;;
        *)
            if [ -z "$BUILD_DIR" ]; then
                BUILD_DIR="$1"
            fi
            shift 1
            ;;
    esac
done
BUILD_DIR="${BUILD_DIR:-/dev/null}"

set -ue

# check if the build directory is valid
[ -L "$BUILD_DIR"/bootstrap.link ] || exit 1

# find compile_commands.json
sourcedir="$(pwd)"
until [ -z "$sourcedir" ] || [ -L "$sourcedir/compile_commands.json" ]; do
	sourcedir="${sourcedir%/*}"
done

# if not found, exit
[ -z "$sourcedir" ] && exit 2

# extract the package name from the compile commands link
x="$(readlink "$sourcedir/compile_commands.json")"
x="${x%/*}"
x="${x##*/}"

# run the lsp server
exec $XBSTRAP -C "$BUILD_DIR" \
    lsp "$x" --extra-tools host-llvm-toolchain -- \
    env HOME=@BUILD_ROOT@/clangd_home \
        XDG_CACHE_HOME=@BUILD_ROOT@/clangd_home/cache \
    clangd -background-index -header-insertion=never \
    --path-mappings \
    @HOST_BUILD_ROOT@=@BUILD_ROOT@,@HOST_SOURCE_ROOT@=@SOURCE_ROOT@
