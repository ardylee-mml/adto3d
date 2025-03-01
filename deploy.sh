#!/bin/bash
echo "Starting deployment..."

# Exit on error
set -e

# Go to project directory
cd ~/2dto3d

# Create Python virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv --without-pip
  source .venv/bin/activate
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  python3 get-pip.py
  rm get-pip.py
else
  # Activate Python virtual environment
  source .venv/bin/activate
fi

# Create and set permissions for necessary directories
echo "Setting up directories..."
mkdir -p uploads outputs logs temp/output

# Set ownership and permissions for directories
echo "Setting permissions..."
# Make current user the owner of all directories
sudo chown -R $USER:$USER uploads outputs logs temp/output
# Set directory permissions to 775 (rwxrwxr-x)
sudo chmod -R 775 uploads outputs logs temp/output
# Add www-data to the current user's group
sudo usermod -a -G $USER www-data

# List directory contents and permissions
echo "Directory permissions:"
ls -la uploads outputs logs temp/output

# Install/update dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip  # Ensure pip is up to date
pip install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build the application
echo "Building frontend..."
npm run build

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
  echo "PM2 is not installed. Installing..."
  sudo npm install -g pm2
fi

# Stop existing services if they're running
pm2 delete all || true
pm2 save

# Start services with explicit paths
echo "Starting frontend service..."
pm2 start npm --name "2dto3d-frontend" -- start

if [ -f app.py ]; then
  echo "Starting backend service..."
  # Start Flask backend with proper environment
  PYTHONPATH=$PWD pm2 start app.py \
    --name "2dto3d-backend" \
    --interpreter python3 \
    --time \
    --log logs/flask.log \
    -- --host=0.0.0.0 --port=5000
fi

# Save PM2 configuration
pm2 save

# Check if services are running
pm2 status

# Display installation status
echo "Checking installations:"
echo "Python packages:"
pip list
echo "Node packages:"
npm list --depth=0

echo "Deployment completed successfully!"
echo "Check logs with: pm2 logs 2dto3d-backend"

# Print the current working directory and file list
echo "Current directory structure:"
pwd
ls -R uploads/
