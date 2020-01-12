FROM debian:buster

ARG USER=1000
RUN apt-get update && apt-get -y install build-essential pkg-config autopoint bison curl flex gettext git gperf help2man m4 mercurial ninja-build python3-mako python3-protobuf python3-yaml texinfo unzip wget xsltproc xz-utils libexpat1-dev rsync python3-pip

RUN pip3 install meson
RUN pip3 install xbstrap

RUN useradd -ms /bin/bash managarm_buildenv -u $USER
USER managarm_buildenv
WORKDIR /home/managarm_buildenv

RUN git config --global user.email "managarm_buildenv@localhost"
RUN git config --global user.name "managarm_buildenv"

CMD ["bash"]
