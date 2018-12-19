# Download source to current directory

git clone https://github.com/noise-lab/iot-inspector-client.git
cd iot-inspector-client/src

# Install global prerequisits

sudo apt install python-pip python-tk git
sudo pip install virtualenv

# Install prerequisits in virtual environment
virtualenv env
source env/bin/activate
pip install elevate netaddr
pip install scapy
pip install scapy-http
pip install scapy-ssl_tls
