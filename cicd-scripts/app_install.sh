#!/bin/bash

# Kill all spider services (if running)
echo "Running app_stop.sh"
sudo chmod +x ./cicd-scripts/app_stop.sh
source ./cicd-scripts/app_stop.sh

# CICD scripts can only runas 'search' user on AWS
if [ "$(whoami)" = "search" ]; then
  echo "Executing cicd scripts as 'search' user"
else
  echo "This script must be executed as 'search' user"
  exit 1
fi

# Get missing packages
sudo apt-get install lzma
sudo apt-get install liblzma-dev
yes | sudo apt-get install libbz2-dev

# Start AWS CloudWatch agent
sudo chmod +x ./cicd-scripts/helpers/check_cloudwatch.sh
source ./cicd-scripts/helpers/check_cloudwatch.sh

# Start AWS CodeDeploy agent
sudo chmod +x ./cicd-scripts/helpers/check_codedeploy.sh
source ./cicd-scripts/helpers/check_codedeploy.sh

# PUBLIC
SPIDER_PYTHON_VERSION=3.12

# PRIVATE
_CURRENT_BUILD_DIR=${PWD}

# Update and upgrade the system without prompting for confirmation
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt install acl -y

# Required to give all app_* bash scripts read/write permissions to self and parent.
# Give current directory and all its files rw permissions
sudo chmod -R 755 .
# All new files/directories will inherit rwx (required when installing and using sqllite)
sudo setfacl -Rdm g:dgsearch:rwx .


# Install necessary system dependencies
sudo apt-get install -y python-setuptools

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

    # Return to the build directory
    cd $_CURRENT_BUILD_DIR

    echo "Python ${SPIDER_PYTHON_VERSION} has been installed."
}

# Check if Python is installed
if command -v python${SPIDER_PYTHON_VERSION} &>/dev/null; then
    echo "Python ${SPIDER_PYTHON_VERSION} is already installed: $(python${SPIDER_PYTHON_VERSION} --version)"
else
    echo "Python ${SPIDER_PYTHON_VERSION} is not installed. Installing Python ${SPIDER_PYTHON_VERSION}..."
    install_python
fi

# Set PYTHONPATH env
source ./cicd-scripts/helpers/update_pythonpath.sh

# Use venv with Python 3.12
sudo /usr/local/bin/python${SPIDER_PYTHON_VERSION} -m pip install --upgrade pip

# Create a virtual environment using Python
echo "Creating python${SPIDER_PYTHON_VERSION} virtual environment..."
sudo /usr/local/bin/python${SPIDER_PYTHON_VERSION} -m venv ./venv

# Activate the virtual environment
source ./venv/bin/activate

# Install all spider dependencies
echo "Installing dependencies..."
sudo pip install --force-reinstall -r ./search_gov_crawler/requirements.txt
sudo pip install pytest-playwright playwright -U
playwright install

echo "Dependencies installed."


# Remove any outstanding app_start.sh reboot cronjobs
echo "Removing any app_start.sh reboot cron jobs..."
crontab -l > cron_backup.bak

# Remove lines containing 'app_start.sh' and update crontab
crontab -l | grep -v 'app_start.sh' > cron_backup_filtered

# Check if there are changes
if cmp -s cron_backup_filtered cron_backup.bak; then
  echo "No cron jobs with 'app_start.sh' found."
else
  sudo crontab cron_backup_filtered
  echo "Cron jobs containing 'app_start.sh' have been removed."
fi

# Clean up temporary files
rm cron_backup_filtered cron_backup.bak

# Add cron job to run the app back up on ec2 restart
echo "Adding app_start.sh reboot cron job..."
sudo chmod +x ./cicd-scripts/app_start.sh

# Define the new cron job
new_cron="@reboot at now + 1 min -f $(pwd)/cicd-scripts/app_start.sh"

# Add the new cron job to the crontab if it's not already present
(crontab -l | grep -v "$new_cron" ; echo "$new_cron") | crontab -

echo "Cron job added: $new_cron"
