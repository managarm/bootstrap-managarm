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
		libexpat1-dev \
		libgmp-dev \
		libmpc-dev \
		libmpfr-dev \
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
		texinfo \
		unzip \
		wget \
		xsltproc \
		xz-utils \
		zlib1g-dev

RUN pip3 install meson \
	&& pip3 install xbstrap

RUN useradd -ms /bin/bash managarm_buildenv -u $USER
USER managarm_buildenv
WORKDIR /home/managarm_buildenv

RUN git config --global user.email "managarm_buildenv@localhost" \
	&& git config --global user.name "managarm_buildenv"

CMD ["bash"]
