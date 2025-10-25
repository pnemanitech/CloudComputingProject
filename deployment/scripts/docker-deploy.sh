#!/bin/bash

# Docker Deployment Script for Image Processing Application
# This script deploys the Django application using Docker

set -e

echo "🐳 Starting Docker Deployment for Image Processing Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker check completed"
}

# Create environment file
create_env_file() {
    print_status "Creating environment file..."
    
    if [ ! -f .env ]; then
        cat > .env <<EOF
# Django Settings
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:password@db:5432/image_processing

# AWS S3 Settings
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_STORAGE_BUCKET_NAME=your-bucket-name-here
AWS_S3_REGION_NAME=us-east-1

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com
EOF
        print_warning "Please update the .env file with your actual values"
    fi
    
    print_status "Environment file created"
}

# Build and start containers
deploy_containers() {
    print_status "Building and starting containers..."
    
    # Stop existing containers
    docker-compose down
    
    # Build and start containers
    docker-compose up --build -d
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec web python manage.py migrate
    
    # Create superuser
    print_status "Creating superuser..."
    docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
"
    
    # Collect static files
    print_status "Collecting static files..."
    docker-compose exec web python manage.py collectstatic --noinput
    
    print_status "Containers deployed successfully"
}

# Show deployment status
show_status() {
    print_status "Deployment Status:"
    docker-compose ps
    
    print_status "Application URLs:"
    echo "  - Main Application: http://localhost"
    echo "  - Admin Panel: http://localhost/admin"
    echo "  - Username: admin"
    echo "  - Password: admin123"
    
    print_status "Useful Commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop services: docker-compose down"
    echo "  - Restart services: docker-compose restart"
    echo "  - Update services: docker-compose up --build -d"
}

# Main deployment function
deploy() {
    print_status "Starting Docker deployment..."
    
    check_docker
    create_env_file
    deploy_containers
    show_status
    
    print_status "Docker deployment completed successfully!"
}

# Run deployment
deploy
