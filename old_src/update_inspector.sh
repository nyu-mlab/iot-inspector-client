#!/bin/bash

#
# Downloads IoT Inspector's binary and starts running it.
#


URL="https://raw.githubusercontent.com/noise-lab/iot-inspector-client/master/v2-src/dist/start_inspector_mac"


mkdir -p ~/princeton-iot-inspector
cd ~/princeton-iot-inspector


download_update()
{
    # Download latest binary as start_inspector_mac.pending
    curl $URL -o start_inspector_mac.download && mv start_inspector_mac.download start_inspector_mac.pending
}


# Called when we're about to start Inspector
if [ "$1" == "pre" ]
then
    # Previously downloaded update didn't exist, so download update.
    if [ ! -f start_inspector_mac.pending ]
    then
        download_update
    fi
    # Make sure we always run the latest update
    cp start_inspector_mac.pending start_inspector_mac
    chmod +x start_inspector_mac
fi


# Called after we have started Inspector
if [ "$1" == "post" ]
then
    download_update
fi


