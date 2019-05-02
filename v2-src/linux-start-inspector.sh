#!/bin/bash

cd ~/princeton-iot-inspector/iot-inspector-client/v2-src/

# Start!
echo "Starting IoT Inspector..."
sudo -E python2 start_inspector.py persistent

# Update software
echo "Updating software..."
git pull

# Install dependencies
echo "Updating depdencies..."
./linux-install-dependencies.sh
