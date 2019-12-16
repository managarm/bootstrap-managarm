
Building a managarm distribution from source
-------------

This repository contains patches and build script to build a [managarm](https://github.com/managarm/managarm) kernel and userspace.

## Build environment

Since it is almost impossible to make sure all build environments will play nice with
the build system, at the moment it is recommended to setup a build environment with Docker
using the provided Dockerfile.

Make sure that you have enough disk space. As managarm builds a lot of large external packages
(like GCC, binutils, coreutils and the Wayland stack), about 20 - 30 GiB are required.

### Creating Docker image and container

This step is not needed if you don't want to use a Docker container, if so skip to the next paragraph.

1.  Install Docker (duh) and make sure it is working properly by running `docker run hello-world`
    and making sure the output shows:
    ```
    Hello from Docker!
    This message shows that your installation appears to be working correctly.
    ```
1.  The following step will create a directory (managarm) in your home directory which will
    be used for storing the source and build directories in order to be able to access them
    at a known location from within the container:
    ```bash
    mkdir ~/managarm && cd ~/managarm
    git clone https://github.com/managarm/bootstrap-managarm.git src
    cd src
    docker build -t managarm_buildenv .
    ```
1.  Start a container:
    ```bash
    docker run -v $(realpath ~/managarm):/home/managarm_buildenv/managarm -it managarm_buildenv
    ```

You are now running a `bash` shell within a Docker container with all the build dependencies
already installed.
Inside the home directory (`ls`) there should be a `managarm` directory shared with the host
containing a `src` directory (this repo).
If this is not the case go back and make sure you followed the steps properly.

Create a `build` directory inside the `managarm` directory:
```bash
cd managarm
mkdir build
```

Now proceed to the Building paragraph.

### Installing dependencies manually

If you created a Docker image in the previous step, skip this paragraph.

1.  Certain programs are required to build managarm;
    here we list the corresponding Debian packages:
    `build-essential`, `pkg-config`, `autopoint`, `bison`, `curl`, `flex`, `gettext`, `git`, `gperf`, `help2man`, `m4`, `mercurial`, `ninja-build`, `python3-mako`, `python3-protobuf`, `python3-yaml`, `texinfo`, `unzip`, `wget`, `xsltproc`, `xz-utils`, `libexpat1-dev`, `rsync`, `python3-pip`.
1.  `meson` is required. There is a Debian package, but as of Debian Stretch, a newer version is required.
    Install it from pip: `pip3 install meson`.
1.  The [xbstrap](https://github.com/managarm/xbstrap) tool is required to build managarm. Install it from pip: `pip3 install xbstrap`.
1.  Clone this repo into a `src` directory and create an empty `build` directory:
    ```bash
    git clone https://github.com/managarm/bootstrap-managarm.git src
    mkdir build
    ```

## Building

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
# It is sufficient to run this once.
../src/scripts/prepare-sysroot

# Create a HDD image file called 'image' and copy the system onto it.
image_create.sh image 2GiB ext2 gpt
../src/scripts/mkimage

# To launch the image using QEMU, you can run:
../src/scripts/run-qemu
```

