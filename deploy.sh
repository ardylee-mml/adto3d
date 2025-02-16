#!/bin/bash
echo "Starting deployment..."

# Go to project directory
cd ~/2dto3d

# Pull latest changes
git pull origin main

# Install dependencies if needed
npm install

# Rebuild the application
npm run build

# Restart the server
pm2 restart 2dto3d

echo "Deployment completed!"
