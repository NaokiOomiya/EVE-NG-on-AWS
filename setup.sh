#!/bin/bash
# Setup a virtual network interface pnet0 if necessary
# sudo ip addr add 192.168.10.10/24 dev pnet0
# sudo ip route add 192.168.0.0/16 via 192.168.10.254

# Unpack migration packages
tar -xvf ./migration_packages.tar.gz
cd ./migration_packages

# Python packages offline installation
pip install -y --no-index --find-links=packages-pip/ -r requirements.txt

# apt packages offline installation
sudo dpkg -i ./packages-apt/*.deb

# show network configuration
echo "---IP addresses for pnet0---"
ip addr show pnet0
echo "---Route table---"
ip route

echo "---Setup completed---"