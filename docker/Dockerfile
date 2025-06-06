#----------------------------------------------------------------------------------------
# "base" stage that contains all packages that we need.
#----------------------------------------------------------------------------------------
FROM debian:bookworm AS base

RUN apt-get update \
	&& apt-get -y install \
		# Don't install recommended stuff
		--no-install-recommends \
		# Used by gnutls
		autogen \
		# Used by host-bison
		autopoint \
		# Used by the Linux kernel
		bc \
		# Used by binutils in the build process
		bison \
		# Contains gcc and g++
		build-essential \
		# Used by several packages
		cmake \
		# Used during image generation
		cpio \
		# Used by protobuf
		curl \
		# Used by binutils in the build process
		flex \
		# Required by flex but not a hard dependency in Debian.
		libfl2 \
		# Used by many tools in the build process
		gawk \
		# Used by libidn2
		gengetopt \
		# Used by host-gettext
		gettext \
		# Git is used extensively in the build process
		git \
		# Used by eudev
		gperf \
		# Used by libiconv
		groff \
		# Used by libtool
		help2man \
		# Used by libdisplay-info
		hwdata \
		# Used by libqalculate
		intltool \
		# Used by shared-mime-info
		itstool \
		# Used by host-karchive
		libbz2-dev \
		liblzma-dev \
		libzstd-dev \
		# Used by host-knotifications
		libcanberra-dev \
		# Used for systemd
		udev \
		# Used by host-appstream
		libcurl4-openssl-dev \
		# Used by the Linux kernel
		libelf-dev \
		# Used by wayland-scanner
		libexpat1-dev \
		# Used by gtk+-2
		libgdk-pixbuf2.0-bin \
		# Used by various gobject tools
		libgirepository1.0-dev \
		# Used by gdk-pixbuf
		libglib2.0-dev-bin \
		# Used by vala
		libglib2.0-dev \
		# Used by gtksourceview5
		libgtk-4-bin \
		# Used by host-qt6
		libgl-dev \
		# Used by GTK4
		libgtk-4-bin \
		# GMP, MPFR and MPC are used by gcc
		libgmp-dev \
		libmpc-dev \
		libmpfr-dev \
		# Used by host-sonnet
		libhunspell-dev \
		# Used by host-kio
		libmount-dev \
		# Used by cmake
		libssl-dev \
		# Used by ace
		libpng-dev \
		# Used by host-solid
		libudev-dev \
		# Used by host-qt6
		libwayland-dev \
		libx11-xcb-dev \
		libxkbcommon-x11-dev \
		# Used by host-kwindowsystem
		libxfixes-dev \
		# Used by host-appstream
		libxml2-dev \
		libyaml-dev \
		# Used by many gnu build steps
		m4 \
		# Required to build images for Android's fastboot protocol.
		mkbootimg \
		# Used by limine
		mtools \
		# Used by libjpeg-turbo for performance reasons
		nasm \
		# Used by groff
		netpbm \
		# Used by Managarm
		ninja-build \
		# To build the certificates, we need trust, provided by p11-kit
		p11-kit \
		# Used by scripts/run-wrapper
		patchelf \
		# Various build systems invoke pkg-config
		pkg-config \
		# Used by host-kguiaddons
		plasma-wayland-protocols \
		# Used by various gobject tools
		python3-gi \
		# Used by libei
		python3-jinja2 \
		# Used by itstool
		python3-libxml2 \
		# Used by mesa
		python3-mako \
		# We need pip, setuptools and wheel for installing python packages
		python3-pip \
		python3-setuptools \
		python3-wheel \
		# Used by host-glib
		python3-packaging \
		# Used by libxcb
		python3-xcbgen \
		# Several programs use rsync
		rsync \
		# Used by webkitgtk
		ruby \
		# Used by GTK4
		sassc \
		# makeinfo is used in gnu build systems
		texinfo \
		# Provides 'mkimage', required to build Allwinner D1 images.
		u-boot-tools \
		# Used by webkitgtk
		unifdef \
		# Used by protobuf
		unzip \
		# Used by host-kwindowsystem
		wayland-protocols \
		# We use wget to fetch some stuff further down
		wget \
		# Used by xcursor-themes
		x11-apps \
		# Used by mutter
		xcvt \
		# Used by eudev
		xsltproc \
		# Used by various programs, for example, it is used by file
		zlib1g-dev \
		# Used by the developers
		clangd \
		# used to generate images
		fdisk \
		dosfstools \
		mtools \
		# Used by host-qt6 to enable the X11 backend
		libxcb-xinerama0-dev \
		libxcb-screensaver0-dev \
		libxcb-composite0-dev \
		libxcb-image0-dev \
		libxcb-record0-dev \
		libxcb-randr0-dev \
		libxcb-present-dev \
		libxcb-damage0-dev \
		libxcb-cursor-dev \
		libxcb-dri3-dev \
		libxcb-dri2-0-dev \
		libxcb-glx0-dev \
		libxcb-xinput-dev \
		libxcb-res0-dev \
		libxcb-xf86dri0-dev \
		libxcb-dpms0-dev \
		libxcb-ewmh-dev \
		libxcb-util0-dev \
		libxcb-keysyms1-dev \
		libxcb-icccm4-dev \
		# Cleanup time
		&& apt-get clean

# Meson is outdated in debian repos, xbstrap is used by the build process.
RUN pip3 install --break-system-packages meson \
	&& pip3 install --break-system-packages xbstrap

# Install mdbook.
RUN cd /root && \
	wget -O mdbook.tar.gz https://github.com/rust-lang/mdBook/releases/download/v0.3.7/mdbook-v0.3.7-x86_64-unknown-linux-gnu.tar.gz && \
	tar xf mdbook.tar.gz && \
	install -D mdbook /usr/local/bin/mdbook

#----------------------------------------------------------------------------------------
# "user" stage that also adds a user account.
#----------------------------------------------------------------------------------------
FROM base AS user
ARG USER=1000

RUN useradd -ms /bin/bash managarm-buildenv -u $USER
USER managarm-buildenv
WORKDIR /home/managarm-buildenv

RUN git config --global user.email "managarm-buildenv@localhost" \
	&& git config --global user.name "managarm-buildenv"

CMD ["bash"]
