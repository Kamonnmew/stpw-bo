#!/bin/bash

echo "Starting custom build script..."

# Install dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Build completed successfully!"
