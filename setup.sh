#!/bin/bash

# Quick Setup Script for Image Processing Application
echo "🚀 Setting up Image Processing Application..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Setting up database..."
python manage.py migrate

# Create superuser (optional)
echo "👤 Creating admin user..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || echo "Admin user already exists"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "🌐 Access the application at: http://localhost:8000"
