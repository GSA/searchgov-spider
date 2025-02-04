#!/bin/bash

# CD into the current script directory (which != $pwd)
cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../

sudo chmod +x ./cicd-scripts/helpers/ensure_executable.sh
source ./cicd-scripts/helpers/ensure_executable.sh

### VARIABLES ###
_CURRENT_BUILD_DIR=${PWD}
VENV_DIR=./venv

### FUNCTIONS ###

# Stop spider services
stop_services() {
    echo "Running app_stop.sh..."
    ensure_executable "./cicd-scripts/app_stop.sh"
}

# Install missing system dependencies
install_system_dependencies() {
    echo "Installing system dependencies..."
    sudo apt-get update -y
    sudo apt-get install -y \
        lzma liblzma-dev libbz2-dev python-setuptools \
        acl build-essential checkinstall libreadline-dev \
        libncursesw5-dev libssl-dev libsqlite3-dev tk-dev \
        libgdbm-dev libc6-dev zlib1g-dev libffi-dev openssl
}

# Install Python
install_python() {
    echo "Installing Python ${SPIDER_PYTHON_VERSION}..."
    cd /usr/src
    sudo wget -q https://www.python.org/ftp/python/${SPIDER_PYTHON_VERSION}.0/Python-${SPIDER_PYTHON_VERSION}.0.tgz
    sudo tar xzf Python-${SPIDER_PYTHON_VERSION}.0.tgz
    sudo chown -R $(whoami) ./Python-${SPIDER_PYTHON_VERSION}.0
    cd Python-${SPIDER_PYTHON_VERSION}.0
    ./configure --enable-optimizations
    sudo make
    sudo make install
    sudo make altinstall
    cd "$_CURRENT_BUILD_DIR"
    echo "Python ${SPIDER_PYTHON_VERSION} installed successfully."
}

# Check and install Python if needed
check_python() {
    if ! command -v python${SPIDER_PYTHON_VERSION} &>/dev/null; then
        install_python
    else
        echo "Python ${SPIDER_PYTHON_VERSION} already installed: $(python${SPIDER_PYTHON_VERSION} --version)"
    fi
}

# Fetch environment variables from parameter store
fetch_env_vars() {
    echo "Fetching environment variables..."
    ensure_executable "./cicd-scripts/helpers/fetch_env_vars.sh"
}

# Set environment paths
update_pythonpath() {
  ensure_executable "./cicd-scripts/helpers/update_pythonpath.sh"
}

# Setup virtual environment
setup_virtualenv() {
    echo "Setting up virtual environment..."
    python${SPIDER_PYTHON_VERSION} -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    python -m pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    python -m pip install --upgrade -r ./search_gov_crawler/requirements.txt
    echo "Installing Playwright..."
    playwright install --with-deps
    playwright install chrome --force
    deactivate
}

# Configure permissions
configure_permissions() {
    echo "Configuring file permissions..."
    sudo chmod -R 777 .
    sudo chown -R "$(whoami)" .
    sudo setfacl -Rdm g:dgsearch:rwx .
}

# Manage cron jobs
manage_cron_jobs() {
    echo "Managing cron jobs..."
    crontab -l | grep -v 'app_start.sh' > temp_cron || true
    echo "@reboot $(pwd)/cicd-scripts/app_start.sh" >> temp_cron
    crontab temp_cron
    rm temp_cron
    echo "Cron jobs updated."
}

# Start monitoring agents
start_agents() {
    echo "Starting AWS CloudWatch agent..."
    ensure_executable "./cicd-scripts/helpers/check_cloudwatch.sh"

    echo "Starting AWS CodeDeploy agent..."
    ensure_executable "./cicd-scripts/helpers/check_codedeploy.sh"
}

### SCRIPT EXECUTION ###

# Stop running services
stop_services

# fetch and export env vars
fetch_env_vars

# Install system dependencies
install_system_dependencies

# Check and install Python if missing
check_python

# Set environment paths
update_pythonpath

# Configure permissions
configure_permissions

# Setup and activate virtual environment
setup_virtualenv

# Install dependencies
install_dependencies

# Start AWS agents
start_agents

# Manage cron jobs
manage_cron_jobs

echo "App installation completed successfully."
