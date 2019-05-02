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
chmod +x linux-install-dependencies.sh
./linux-install-dependencies.sh

# Mark linux start script as executable
chmod +x linux-start-inspector.sh
ln -s ~/princeton-iot-inspector/iot-inspector-client/v2-src/linux-start-inspector.sh ~/princeton-iot-inspector/linux-start-inspector.sh

echo "=================================================================="
echo ""
echo "Setup complete."
echo ""
echo "To start, run ~/princeton-iot-inspector/linux-start-inspector.sh."
echo ""
echo "=================================================================="
