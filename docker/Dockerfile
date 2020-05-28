FROM debian:buster

ARG USER=1000
RUN apt-get update \
	&& apt-get -y install \
		autopoint \
		bison \
		build-essential \
		curl \
		doxygen \
		flex \
		gettext \
		git \
		gperf \
		help2man \
		itstool \
		libarchive-dev \
		libexpat1-dev \
		libgmp-dev \
		libmpc-dev \
		libmpfr-dev \
		libssl-dev \
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
		rsync \
		subversion \
		texinfo \
		unzip \
		wget \
		xsltproc \
		xz-utils \
		zlib1g-dev

RUN pip3 install meson \
	&& pip3 install xbstrap

# Install xbps from source (there is no Debian package).
RUN cd /root/ \
	&& wget https://github.com/void-linux/xbps/archive/0.59.1.tar.gz \
	&& tar -xzf 0.59.1.tar.gz \
	&& cd xbps-0.59.1/ \
	&& ./configure --enable-rpath && make && make install

RUN useradd -ms /bin/bash managarm_buildenv -u $USER
USER managarm_buildenv
WORKDIR /home/managarm_buildenv

RUN git config --global user.email "managarm_buildenv@localhost" \
	&& git config --global user.name "managarm_buildenv"

CMD ["bash"]
