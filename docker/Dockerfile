
FROM debian:stable
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git
RUN apt-get install -y python3-pip make ninja-build flex bison
RUN apt-get install -y curl help2man texinfo m4 unzip
RUN pip3 install meson
RUN git config --global user.email "nobody@example.com" && git config --global user.name "Nobody"
RUN git clone https://github.com/managarm/xbstrap.git
RUN git clone https://github.com/managarm/bootstrap-managarm.git
RUN cd xbstrap && pip3 install .
RUN mkdir build-root && cd build-root && xbstrap init ../bootstrap-managarm
RUN cd build-root && xbstrap install-tool --all && rm -rf ../bootstrap-managarm/src/{managarm,mlibc,ports} && rm -rf pkg-builds
WORKDIR /build-root
ENTRYPOINT ["xbstrap"]

