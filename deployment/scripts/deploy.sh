#!/bin/bash

# Image Processing Application Deployment Script
# This script deploys the Django application to production

set -e

echo "🚀 Starting Image Processing Application Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="image-processing-app"
APP_DIR="/opt/$APP_NAME"
SERVICE_USER="django"
SERVICE_GROUP="django"

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root"
    exit 1
fi

# Check if required commands exist
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed"
        exit 1
    fi
    
    if ! command -v nginx &> /dev/null; then
        print_warning "Nginx is not installed. Installing..."
        sudo apt-get update
        sudo apt-get install -y nginx
    fi
    
    print_status "Requirements check completed"
}

# Create application directory
setup_directories() {
    print_status "Setting up directories..."
    
    sudo mkdir -p $APP_DIR
    sudo mkdir -p /var/log/$APP_NAME
    sudo mkdir -p /etc/$APP_NAME
    
    # Create service user if it doesn't exist
    if ! id "$SERVICE_USER" &>/dev/null; then
        sudo useradd --system --shell /bin/bash --home $APP_DIR --create-home $SERVICE_USER
    fi
    
    sudo chown -R $SERVICE_USER:$SERVICE_GROUP $APP_DIR
    sudo chown -R $SERVICE_USER:$SERVICE_GROUP /var/log/$APP_NAME
    
    print_status "Directories setup completed"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    cd $APP_DIR
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_status "Dependencies installed"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    cd $APP_DIR
    source venv/bin/activate
    
    # Run migrations
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    if ! python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists()" | grep -q True; then
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell
    fi
    
    print_status "Database setup completed"
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    
    cd $APP_DIR
    source venv/bin/activate
    
    python manage.py collectstatic --noinput
    
    print_status "Static files collected"
}

# Setup systemd service
setup_systemd() {
    print_status "Setting up systemd service..."
    
    sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null <<EOF
[Unit]
Description=Image Processing Django Application
After=network.target

[Service]
Type=notify
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$APP_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
Environment=SECRET_KEY=$(openssl rand -base64 32)
Environment=DEBUG=False
ExecStart=$APP_DIR/venv/bin/gunicorn --bind unix:$APP_DIR/$APP_NAME.sock config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable $APP_NAME
    sudo systemctl start $APP_NAME
    
    print_status "Systemd service setup completed"
}

# Setup Nginx
setup_nginx() {
    print_status "Setting up Nginx..."
    
    sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location /static/ {
        alias $APP_DIR/staticfiles/;
    }
    
    location /media/ {
        alias $APP_DIR/media/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/$APP_NAME.sock;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl restart nginx
    
    print_status "Nginx setup completed"
}

# Main deployment function
deploy() {
    print_status "Starting deployment process..."
    
    check_requirements
    setup_directories
    install_dependencies
    setup_database
    collect_static
    setup_systemd
    setup_nginx
    
    print_status "Deployment completed successfully!"
    print_status "Application is running at: http://$(curl -s ifconfig.me)"
    print_status "Admin panel: http://$(curl -s ifconfig.me)/admin/"
    print_status "Username: admin, Password: admin123"
}

# Run deployment
deploy
