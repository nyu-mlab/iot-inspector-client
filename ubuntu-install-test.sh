# Install global prerequisits

sudo apt install python-pip git
sudo pip install virtualenv

# Download source to current directory

git clone https://github.com/noise-lab/iot-inspector-client.git
cd iot-inspector-client/v2-src

# Install prerequisits in virtual environment
virtualenv env
source env/bin/activate
pip install Flask
pip install flask_cors
pip install requests
pip install elevate netaddr
pip install scapy-ssl_tls
pip install scapy-http

# Download sample profile
cd ~
wget 'https://iot-inspector.princeton.edu/tmp/iot_inspector_config.json'
