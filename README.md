
Building a managarm distribution from source
-------------

This repository contains patches and build script to build a [managarm](https://github.com/managarm/managarm) kernel and userspace.

## Prerequisites

1.  Certain porgrams are required to build managarm;
    here we list the corresponding Debian packages:
    `bison`, `curl`, `flex`, `git`, `help2man`, `m4`, `make`, `ninja-build`, `texinfo`, `unzip`, `wget`, `xz-utils`.
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
