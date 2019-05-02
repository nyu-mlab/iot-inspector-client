#!/bin/bash

# The following line works for Debian only.
sudo apt update
sudo apt install python-pip python3-pip git

# Create inspector directory
mkdir ~/princeton-iot-inspector

# Download source
cd ~/princeton-iot-inspector
git clone https://github.com/noise-lab/iot-inspector-client

# Install python dependencies
cd ~/princeton-iot-inspector/iot-inspector-client/v2-src
bash ./linux-install-dependencies.sh

# Create symbolic link for the main entry script
ln -s ~/princeton-iot-inspector/iot-inspector-client/v2-src/linux-start-inspector.sh ~/princeton-iot-inspector/linux-start-inspector.sh

echo "=================================================================="
echo ""
echo "Setup complete."
echo ""
echo "To start, run: "
echo "  sudo ~/princeton-iot-inspector/linux-start-inspector.sh"
echo ""
echo "=================================================================="
