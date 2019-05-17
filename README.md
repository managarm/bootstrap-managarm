
Building a managarm distribution from source
-------------

This repository contains patches and build script to build a [managarm](https://github.com/managarm/managarm) kernel and userspace.

## Prerequisites

1.  Certain programs are required to build managarm;
    here we list the corresponding Debian packages:
    `bison`, `curl`, `flex`, `gettext`, `git`, `gpref`, `help2man`, `m4`, `make`, `ninja-build`, `python-mako` (host dependency of Mesa), `texinfo`, `unzip`,
	`libwayland-dev`, `wget`, `xsltproc`, `xz-utils`.
    Furthermore, `meson` is required. There is a Debian package, but as of Debian Stretch, a newer version is required.
    Install it from pip using `pip3 install meson`.
1.  The [xbstrap](https://github.com/managarm/xbstrap) tool is required to build managarm. Install it from pip.
1.  Make sure that you have enough disk space. As managarm builds a lot of large external packages
    (like GCC, binutils, coreutils and the Wayland stack), about 20 - 30 GiB are required.

## Building

1.  Clone this repository into a `src` directory and create a `build` directory
    (perferably at the same level; the actual names do not matter).
    Thus, your directory structure should look like this:<br>
    `src/`: This repository.<br>
    `build/`: An empty directory.
1.  Change into the build directory
    ```
    cd build/
    ```
1.  Initialize the build directory with
    ```
    xbstrap init ../src
    ```
1.  Start the build using
    ```
    xbstrap install --all
    ```
    Note that this command can take multiple hours, depending on your machine.

Altogether, those commands are:
```
git clone https://github.com/managarm/bootstrap-managarm.git src/
mkdir build/ && cd build/
xbstrap init ../src
xbstrap install --all
```

## Creating Images

After managarm's packages have been built, building a HDD image of the system
is straightforward. The [image_create.sh](https://gitlab.com/qookei/image_create) script
can be used to create an empty HDD image. This repository contains a `mkimage` script
to copy the system onto the image. Note that `mkimage` requires `libguestfs`
to be able to create an image without requiring root access.

Hence, running the following commands in the build directory
should produce a working image and launch it using QEMU:
```
# Copy some files (e.g., the timezone configuration) from the host to system-root/.
# This sufficient to run this once
../src/scripts/prepare-sysroot

# Create a HDD image file called 'image' and copy the system onto it.
image_create.sh image 2GiB ext2 gpt
../src/scripts/mkimage

# To launch the image using QEMU, you can run:
../src/scripts/run-qemu
```

