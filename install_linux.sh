#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
SOURCE="$(readlink "$SOURCE")"
[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

cd $DIR && \
mkdir -p /etc/iot-inspector && \
cp installation_files/iot-inspector.conf /etc/iot-inspector/iot-inspector.conf && \
cp installation_files/iot-inspector.service /lib/systemd/system/iot-inspector.service && \
chmod 644 /lib/systemd/system/iot-inspector.service && \
chown root:root /lib/systemd/system/iot-inspector.service && \
cp -r src /opt/iot-inspector && \
/opt/iot-inspector/linux-install-dependencies.sh && \
echo "Successfully installed the iot-inspector to /opt/iot-inspector. You can start the iot-inspector by typing 'systemctl start iot-inspector.service'."
