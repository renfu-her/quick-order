#!/bin/bash
# Deployment Script for Quick Orders System

echo "=== Quick Orders Deployment Script ==="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as root"
    exit 1
fi

# Set variables
PROJECT_DIR="/home/renfu/htdocs/py-sites/shop"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"

# Create directories if they don't exist
echo "Creating directories..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/uploads"

# Copy project files (assuming you're running from the project directory)
echo "Copying project files..."
cp -r application "$PROJECT_DIR/"
cp -r templates "$PROJECT_DIR/"
cp -r static "$PROJECT_DIR/"
cp -r routes "$PROJECT_DIR/"
cp -r models "$PROJECT_DIR/"
cp -r migrations "$PROJECT_DIR/"
cp -r scripts "$PROJECT_DIR/"
cp wsgi.py "$PROJECT_DIR/"
cp gunicorn.conf.py "$PROJECT_DIR/"
cp config_production.py "$PROJECT_DIR/"
cp requirements.txt "$PROJECT_DIR/"

# Set up virtual environment
echo "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Set up database
echo "Setting up database..."
cd "$PROJECT_DIR"
export FLASK_APP=wsgi.py
flask db upgrade

# Set permissions
echo "Setting permissions..."
chmod +x "$PROJECT_DIR/wsgi.py"
chmod +x "$PROJECT_DIR/gunicorn.conf.py"

echo "=== Deployment completed successfully ==="
echo "To start the server:"
echo "cd $PROJECT_DIR"
echo "source venv/bin/activate"
echo "gunicorn -c gunicorn.conf.py wsgi:app"
