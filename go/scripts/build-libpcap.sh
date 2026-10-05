#!/usr/bin/env bash
# Build a minimal static libpcap for linux release binaries, so they only
# depend on glibc (distro libpcap sonames differ: .so.0.8 on debian, .so.1 elsewhere).
# Usage: build-libpcap.sh <install-prefix>
set -euo pipefail

VERSION=1.10.7
SHA256=68fa62cffb974f4275641ce14c2e2d75739251f30e00e6a0900903b247d76a03
PREFIX=${1:?usage: build-libpcap.sh <install-prefix>}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"

curl -fsSL -o libpcap.tar.xz "https://www.tcpdump.org/release/libpcap-$VERSION.tar.xz"
echo "$SHA256  libpcap.tar.xz" | sha256sum -c -
tar xf libpcap.tar.xz
cd "libpcap-$VERSION"

# capture over plain linux sockets only; no dbus/rdma/bluetooth/netlink deps
./configure --prefix="$PREFIX" --disable-shared --enable-static \
  --disable-dbus --disable-rdma --disable-bluetooth --disable-usb \
  --disable-netmap --without-libnl --without-dag --without-septel \
  --without-snf --without-turbocap --disable-remote >/dev/null
make -j"$(nproc)" >/dev/null
make install >/dev/null
echo "libpcap $VERSION installed to $PREFIX"
