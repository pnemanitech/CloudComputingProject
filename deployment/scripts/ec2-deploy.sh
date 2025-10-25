#!/bin/bash

# AWS EC2 Deployment Script for Image Processing Application
# This script automates the deployment process on EC2

set -e

echo "☁️ Starting AWS EC2 Deployment for Image Processing Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="image-processing"
APP_DIR="/opt/$APP_NAME"
SERVICE_USER="ubuntu"
SERVICE_GROUP="ubuntu"
DB_NAME="image_processing"
DB_USER="django"

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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
}

# Update system packages
update_system() {
    print_step "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_status "System updated"
}

# Install system dependencies
install_dependencies() {
    print_step "Installing system dependencies..."
    
    sudo apt install -y \
        python3.9 python3.9-venv python3.9-dev python3-pip \
        postgresql postgresql-contrib \
        nginx \
        supervisor \
        redis-server \
        libpq-dev \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        curl wget git vim htop \
        ufw
    
    print_status "Dependencies installed"
}

# Setup PostgreSQL
setup_database() {
    print_step "Setting up PostgreSQL database..."
    
    # Start PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\q
EOF
    
    print_status "Database setup completed"
}

# Create application directory
setup_app_directory() {
    print_step "Setting up application directory..."
    
    sudo mkdir -p $APP_DIR
    sudo chown -R $SERVICE_USER:$SERVICE_GROUP $APP_DIR
    
    print_status "Application directory created"
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    cd $APP_DIR
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    print_status "Python dependencies installed"
}

# Configure environment
setup_environment() {
    print_step "Setting up environment variables..."
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -base64 32)
    
    # Create environment file
    cat > $APP_DIR/.env <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,$(curl -s ifconfig.me)
DATABASE_URL=postgresql://$DB_USER:secure_password_123@localhost:5432/$DB_NAME
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_STORAGE_BUCKET_NAME=your-bucket-name-here
AWS_S3_REGION_NAME=us-east-1
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com
REDIS_URL=redis://127.0.0.1:6379/1
EOF
    
    print_warning "Please update the .env file with your actual AWS and email credentials"
    print_status "Environment file created"
}

# Setup Django application
setup_django() {
    print_step "Setting up Django application..."
    
    cd $APP_DIR
    source venv/bin/activate
    
    # Set environment
    export DJANGO_SETTINGS_MODULE=config.settings.production
    
    # Run migrations
    python manage.py migrate
    
    # Create superuser
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    print_status "Django application setup completed"
}

# Create Gunicorn configuration
setup_gunicorn() {
    print_step "Setting up Gunicorn configuration..."
    
    cat > $APP_DIR/gunicorn.conf.py <<EOF
bind = "unix:$APP_DIR/$APP_NAME.sock"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
    
    print_status "Gunicorn configuration created"
}

# Create systemd service
setup_systemd() {
    print_step "Setting up systemd service..."
    
    sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null <<EOF
[Unit]
Description=Image Processing Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$APP_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # Start service
    sudo systemctl daemon-reload
    sudo systemctl enable $APP_NAME
    sudo systemctl start $APP_NAME
    
    print_status "Systemd service created and started"
}

# Configure Nginx
setup_nginx() {
    print_step "Setting up Nginx configuration..."
    
    sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Client max body size for file uploads
    client_max_body_size 100M;
    
    # Static files
    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias $APP_DIR/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Django application
    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/$APP_NAME.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and restart nginx
    sudo nginx -t
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    print_status "Nginx configured and started"
}

# Configure firewall
setup_firewall() {
    print_step "Setting up firewall..."
    
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    sudo ufw --force enable
    
    print_status "Firewall configured"
}

# Start Redis
setup_redis() {
    print_step "Starting Redis..."
    
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    print_status "Redis started"
}

# Show deployment status
show_status() {
    print_step "Deployment Status:"
    
    echo "✅ Application Status:"
    sudo systemctl status $APP_NAME --no-pager -l
    
    echo "✅ Nginx Status:"
    sudo systemctl status nginx --no-pager -l
    
    echo "✅ Database Status:"
    sudo systemctl status postgresql --no-pager -l
    
    echo "✅ Redis Status:"
    sudo systemctl status redis-server --no-pager -l
    
    echo "✅ Application URLs:"
    echo "  - Main Application: http://$(curl -s ifconfig.me)"
    echo "  - Admin Panel: http://$(curl -s ifconfig.me)/admin/"
    echo "  - Health Check: http://$(curl -s ifconfig.me)/health/"
    echo "  - Username: admin"
    echo "  - Password: admin123"
    
    echo "✅ Useful Commands:"
    echo "  - View logs: sudo journalctl -u $APP_NAME -f"
    echo "  - Restart app: sudo systemctl restart $APP_NAME"
    echo "  - Check status: sudo systemctl status $APP_NAME"
    echo "  - View nginx logs: sudo tail -f /var/log/nginx/error.log"
}

# Main deployment function
deploy() {
    print_status "Starting EC2 deployment process..."
    
    check_root
    update_system
    install_dependencies
    setup_database
    setup_app_directory
    install_python_deps
    setup_environment
    setup_django
    setup_gunicorn
    setup_systemd
    setup_nginx
    setup_firewall
    setup_redis
    show_status
    
    print_status "EC2 deployment completed successfully!"
    print_warning "Don't forget to:"
    print_warning "1. Update .env file with your actual AWS credentials"
    print_warning "2. Configure your domain DNS if using a custom domain"
    print_warning "3. Set up SSL certificate with: sudo certbot --nginx -d your-domain.com"
}

# Run deployment
deploy
