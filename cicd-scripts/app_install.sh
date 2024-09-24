#!/bin/bash


# A hack to get the environment running without ansible local env variables
# This block of code will eventually be removed once ansible task is completed
SPIDER_PYTHON_VERSION=3.12
SPIDER_STAGING_URLS_API=https://staging.search.usa.gov/urls
spider_local_path=/etc/profile.d/spider_local.sh

# Writing environment variables to the profile file
echo "
export SPIDER_PYTHON_VERSION=${SPIDER_PYTHON_VERSION}
export SPIDER_STAGING_URLS_API=${SPIDER_STAGING_URLS_API}
" | tee "$spider_local_path" > /dev/null

# Source the script to update the current shell's environment
source "$spider_local_path"
### TODO: Remove the above code block after ansible is fully implmented


# Update and upgrade the system without prompting for confirmation
sudo apt-get update -y
sudo apt-get upgrade -y

# Install necessary system dependencies
sudo apt-get install -y python-setuptools python-pip

install_python() {
    echo "Installing ${SPIDER_PYTHON_VERSION}"
    sudo apt-get install -y build-essential checkinstall libreadline-dev \
                            libncursesw5-dev libssl-dev libsqlite3-dev \
                            tk-dev libgdbm-dev libc6-dev libbz2-dev \
                            zlib1g-dev openssl libffi-dev

    # Download Python source code
    cd /usr/src
    sudo wget https://www.python.org/ftp/python/${SPIDER_PYTHON_VERSION}.0/Python-${SPIDER_PYTHON_VERSION}.0.tgz
    sudo tar xzf Python-${SPIDER_PYTHON_VERSION}.0.tgz

    # Build and install Python
    cd Python-${SPIDER_PYTHON_VERSION}.0
    sudo ./configure --enable-optimizations
    sudo make altinstall

    echo "Python ${SPIDER_PYTHON_VERSION} has been installed."
}

# Check if Python is installed
if command -v python${SPIDER_PYTHON_VERSION} &>/dev/null; then
    echo "Python ${SPIDER_PYTHON_VERSION} is already installed: $(python${SPIDER_PYTHON_VERSION} --version)"
else
    echo "Python ${SPIDER_PYTHON_VERSION} is not installed. Installing Python ${SPIDER_PYTHON_VERSION}..."
    install_python
fi

# Install virtualenv using Python pip
sudo /usr/local/bin/python${SPIDER_PYTHON_VERSION} -m pip install --upgrade pip
sudo /usr/local/bin/python${SPIDER_PYTHON_VERSION} -m pip install virtualenv

# Navigate to the spider directory
cd /home/ec2-user/spider

# Create a virtual environment using Python
echo "Creating pytho${SPIDER_PYTHON_VERSION} virtual environment..."
/usr/local/bin/python${SPIDER_PYTHON_VERSION} -m venv /home/ec2-user/spider/venv

# Activate the virtual environment
source /home/ec2-user/spider/venv/bin/activate

# Install all spider dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install --upgrade --force-reinstall -r ./search_gov_crawler/requirements.txt

echo "Dependencies installed."
