#!/bin/bash

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-setuptools
sudo apt-get install python-pip

# Function to install Python 3.12
install_python() {
    echo "Installing Python 3.12..."
    sudo apt update
    sudo apt install -y build-essential checkinstall
    sudo apt install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev \
                        libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
                        zlib1g-dev openssl libffi-dev

    # Download Python 3.12 source code
    cd /usr/src
    sudo wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
    sudo tar xzf Python-3.12.0.tgz

    # Build and install
    cd Python-3.12.0
    sudo ./configure --enable-optimizations
    sudo make altinstall

    echo "Python 3.12 has been installed."
}

# Check if Python 3.12 is installed
python_version=$(python3 --version 2>&1)

if [[ $python_version == *"3.12"* ]]; then
    echo "Python 3.12 is already installed: $python_version"
else
    echo "Current Python version: $python_version"
    echo "Installing Python 3.12..."
    install_python
fi



# Creating python3.12 virtual env

pip install virtualenv

cd /home/ec2-user/spider

echo "Creating python3.12 virtual environment..."
python3.12 -m venv /home/ec2-user/spider/venv
source /home/ec2-user/spider/venv/bin/activate

# Installing all spider dependencies
echo "Installing dependencies..."
pip install --upgrade pip

pip install --upgrade --force-reinstall -r ./search_gov_crawler/requirements.txt

echo "Dependencies installed."
