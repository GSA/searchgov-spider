#!/bin/bash

# Update and upgrade the system without prompting for confirmation
sudo apt-get update -y
sudo apt-get upgrade -y

# Install necessary system dependencies
sudo apt-get install -y python-setuptools python-pip

# Function to install Python 3.12
install_python() {
    echo "Installing Python 3.12..."
    sudo apt-get install -y build-essential checkinstall libreadline-dev \
                            libncursesw5-dev libssl-dev libsqlite3-dev \
                            tk-dev libgdbm-dev libc6-dev libbz2-dev \
                            zlib1g-dev openssl libffi-dev

    # Download Python 3.12 source code
    cd /usr/src
    sudo wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
    sudo tar xzf Python-3.12.0.tgz

    # Build and install Python 3.12
    cd Python-3.12.0
    sudo ./configure --enable-optimizations
    sudo make altinstall

    echo "Python 3.12 has been installed."
}

# Check if Python 3.12 is installed
if command -v python3.12 &>/dev/null; then
    echo "Python 3.12 is already installed: $(python3.12 --version)"
else
    echo "Python 3.12 is not installed. Installing Python 3.12..."
    install_python
fi

# Install virtualenv using Python 3.12's pip
sudo /usr/local/bin/python3.12 -m pip install --upgrade pip
sudo /usr/local/bin/python3.12 -m pip install virtualenv

# Navigate to the spider directory
cd /home/ec2-user/spider

# Create a virtual environment using Python 3.12
echo "Creating python3.12 virtual environment..."
/usr/local/bin/python3.12 -m venv /home/ec2-user/spider/venv

# Activate the virtual environment
source /home/ec2-user/spider/venv/bin/activate

# Install all spider dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install --upgrade --force-reinstall -r ./search_gov_crawler/requirements.txt

echo "Dependencies installed."
