
# Building a managarm distribution from source

![Sanity Checks](https://github.com/managarm/bootstrap-managarm/workflows/Sanity%20Checks/badge.svg)

This repository contains patches and build script to build a [managarm](https://github.com/managarm/managarm) kernel and userspace.

## Build environment

Since it is almost impossible to make sure all build environments will play nice with
the build system, at the moment it is recommended to setup a build environment with Docker
using the provided Dockerfile.

Make sure that you have enough disk space. As managarm builds a lot of large external packages
(like GCC, binutils, coreutils and the Wayland stack), about 20 - 30 GiB are required.

### Preparations

First and foremost we will create a directory (`$MANAGARM_DIR`) which will be used for storing the source
and build directories.
```bash
export MANAGARM_DIR="$HOME/managarm" # In this example we are using $HOME/managarm, but it can be any directory
mkdir -p "$MANAGARM_DIR" && cd "$MANAGARM_DIR"
```
Then clone this repository into a `src` directory:
```bash
git clone https://github.com/managarm/bootstrap-managarm.git src
```

### Creating Docker image and container

*Note: this step is not needed if you don't want to use a Docker container, if so skip to the next paragraph.*

1.  Install Docker (duh) and make sure it is working properly by running `docker run hello-world`
    and making sure the output shows:
    ```
    Hello from Docker!
    This message shows that your installation appears to be working correctly.
    ```
1.  Create a Docker image from the provided Dockerfile:
    ```bash
    docker build -t managarm_buildenv src/docker
    ```
1.  Start a container:
    ```bash
    docker run -v $(realpath "$MANAGARM_DIR"):/home/managarm_buildenv/managarm -it managarm_buildenv
    ```

You are now running a `bash` shell within a Docker container with all the build dependencies
already installed.
Inside the home directory (`ls`) there should be a `managarm` directory shared with the host
containing a `src` directory (this repo).
If this is not the case go back and make sure you followed the steps properly.

Switch to the `managarm` directory:
```bash
cd managarm
```
Now proceed to the Building paragraph.

### Installing dependencies manually

*Note: if you created a Docker image in the previous step, skip this paragraph.*

1.  Certain programs are required to build managarm;
    here we list the corresponding Debian packages:
    `build-essential`, `pkg-config`, `autopoint`, `bison`, `curl`, `flex`, `gettext`, `git`, `gperf`, `help2man`, `m4`, `mercurial`, `ninja-build`, `python3-mako`, `python3-protobuf`, `python3-yaml`, `texinfo`, `unzip`, `wget`, `xsltproc`, `xz-utils`, `libexpat1-dev`, `rsync`, `python3-pip`, `python3-libxml2`, `netpbm`, `itstool`, `zlib1g-dev`, `libgmp-dev`, `libmpfr-dev`, `libmpc-dev`, `subversion`, `gawk`, `libwayland-bin`, `libpng-dev`, `gtk-doc-tools`, `groff`, `libglib2.0-dev-bin`.
1.  `meson` is required. There is a Debian package, but as of Debian Stretch, a newer version is required.
    Install it from pip: `pip3 install meson`.
1.  The [xbstrap](https://github.com/managarm/xbstrap) and [bragi](https://github.com/managarm/bragi) tools are required to build managarm. Install them via pip: `pip3 install bragi xbstrap`.

## Building

1.  Create and change into a `build` directory
    ```bash
    mkdir build && cd build
    ```
1.  Initialize the build directory with
    ```bash
    xbstrap init ../src
    ```
1.  Start the build using
    ```bash
    xbstrap install --all
    ```
    Note that this command can take multiple hours, depending on your machine.

## Creating Images

*Note: if using a Docker container the following commands are meant to be ran* **_outside_**
*the Docker container, in the `build` directory on the host.*
*Adding to the aforementioned commands, one would `exit` from the container once*
*the build finishes, enter the `build` directory, and proceed as follows.*

After managarm's packages have been built, building a HDD image of the system
is straightforward. The [image_create.sh](https://gitlab.com/qookei/image_create) script
can be used to create an empty HDD image.

Download the `image_create.sh` script and mark it executable:
```bash
wget 'https://gitlab.com/qookei/image_create/raw/master/image_create.sh'
chmod +x image_create.sh
```

This repository contains a `mkimage` script
to copy the system onto the image. Note that `mkimage` requires `libguestfs`
and `rsync` to be able to create an image without requiring root access and synchronise it.

After installing `libguestfs` it might be necessary to run the following:
```bash
sudo install -d /usr/lib/guestfs
sudo update-libguestfs-appliance
```

Hence, running the following commands in the build directory
should produce a working image and launch it using QEMU:
```bash
# Create a HDD image file called 'image' and copy the system onto it.
./image_create.sh image 4GiB ext2 gpt
../src/scripts/mkimage

# To launch the image using QEMU, you can run:
../src/scripts/run-qemu
```

