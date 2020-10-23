#----------------------------------------------------------------------------------------
# "base" stage that contains all packages that we need.
#----------------------------------------------------------------------------------------
FROM debian:buster AS base

RUN apt-get update \
	&& apt-get -y install \
		autopoint \
		bison \
		build-essential \
		curl \
		doxygen \
		flex \
		gawk \
		gettext \
		git \
		gperf \
		groff \
		gtk-doc-tools \
		help2man \
		itstool \
		libarchive-dev \
		libexpat1-dev \
		libglib2.0-dev-bin \
		libgmp-dev \
		libmpc-dev \
		libmpfr-dev \
		libssl-dev \
		libpng-dev \
		libwayland-bin \
		m4 \
		mercurial \
		netpbm \
		ninja-build \
		pkg-config \
		python3-libxml2 \
		python3-mako \
		python3-pip \
		python3-protobuf \
		python3-yaml \
		ragel \
		rsync \
		subversion \
		texinfo \
		unzip \
		wget \
		xsltproc \
		xz-utils \
		zlib1g-dev

RUN pip3 install meson \
	&& pip3 install xbstrap \
	&& pip3 install bragi

# Install xbps from source (there is no Debian package).
RUN cd /root/ \
	&& wget https://github.com/void-linux/xbps/archive/0.59.1.tar.gz \
	&& tar -xzf 0.59.1.tar.gz \
	&& cd xbps-0.59.1/ \
	&& ./configure --enable-rpath && make && make install

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

RUN useradd -ms /bin/bash managarm_buildenv -u $USER
USER managarm_buildenv
WORKDIR /home/managarm_buildenv

RUN git config --global user.email "managarm_buildenv@localhost" \
	&& git config --global user.name "managarm_buildenv"

CMD ["bash"]
