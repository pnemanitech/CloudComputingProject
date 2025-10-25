#!/bin/bash

# Image Processing Application Deployment Script
# This script sets up the Django application for production deployment

echo "🚀 Starting Image Processing Application Deployment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static
mkdir -p media/original_images
mkdir -p media/processed_images

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📊 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Creating superuser (optional)..."
echo "You can create a superuser account for admin access."
echo "Run: python manage.py createsuperuser"

echo "✅ Deployment completed successfully!"
echo ""
echo "To start the development server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run server: python manage.py runserver"
echo "3. Open browser: http://127.0.0.1:8000"
echo ""
echo "For production deployment, see README.md for detailed instructions."
