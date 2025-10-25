# 🖼️ Image Processing Application

A cloud-based Django application for processing images with various filters and storing them in AWS S3.

## ✨ Features

- **6 Image Filters**: Grayscale, Sepia, Poster, Blur, Edge Detection, Solar
- **Drag & Drop Upload**: Easy image upload interface
- **AWS S3 Integration**: Automatic cloud storage
- **Responsive Design**: Works on desktop and mobile
- **Docker Support**: Easy deployment with Docker
- **Gallery View**: Browse all processed images

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
git clone https://github.com/pneman1/CloudImage.git
cd CloudImage
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python manage.py runserver
```

### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pneman1/CloudImage.git
   cd CloudImage
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Main app: http://localhost:8000
   - Upload images: http://localhost:8000/images/upload/
   - Gallery: http://localhost:8000/images/gallery/

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Main app: http://localhost:8000
   - Nginx proxy: http://localhost:80

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/image_processing

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

### AWS S3 Setup

1. **Create S3 bucket**
   ```bash
   ./setup-s3.sh
   ```

2. **Or configure manually**
   ```bash
   aws configure
   ```

3. **Test S3 integration**
   - Upload an image through the web interface
   - Check your S3 bucket for the processed image

## 📁 Project Structure

```
ImageProcessing/
├── apps/                    # Django applications
│   ├── core/               # Core functionality
│   ├── images/             # Image processing
│   ├── storage/            # S3 storage utilities
│   └── common/             # Shared utilities
├── config/                 # Django configuration
├── templates/              # HTML templates
├── static/                # Static files (CSS, JS)
├── media/                  # Media files
├── deployment/             # Deployment configurations
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
└── manage.py              # Django management script
```

## 🎨 Image Filters

The application supports 6 different image filters:

1. **Grayscale** - Convert to black and white
2. **Sepia** - Vintage brown tone effect
3. **Poster** - Reduce colors for poster effect
4. **Blur** - Gaussian blur effect
5. **Edge Detection** - Highlight edges
6. **Solar** - Invert colors for solar effect

## 🚀 Deployment

### Local Docker Deployment

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

1. **Configure environment variables**
   ```bash
   cp production.env.example .env
   # Edit .env with your production values
   ```

2. **Deploy with production configuration**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Set up SSL (optional)**
   - Configure Nginx with SSL certificates
   - Update security settings in Django

## 🔧 Development

### Running Tests

```bash
python manage.py test
```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Static Files

```bash
# Collect static files
python manage.py collectstatic
```

## 📊 Monitoring

### Logs

- **Django logs**: Check console output
- **Docker logs**: `docker-compose logs -f`
- **Nginx logs**: `docker-compose logs nginx`

### Performance

- **Image processing**: Optimized with NumPy
- **S3 uploads**: Asynchronous processing
- **Caching**: Redis for session storage

## 🛠️ Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**
   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`

2. **"Database connection failed"**
   - Check database configuration
   - Run migrations: `python manage.py migrate`

3. **"S3 upload failed"**
   - Verify AWS credentials
   - Check S3 bucket permissions
   - Ensure bucket exists

4. **"Static files not found"**
   - Run: `python manage.py collectstatic`
   - Check STATIC_ROOT setting

### Debug Mode

Enable debug mode for development:

```python
# In config/settings.py
DEBUG = True
```

## 📝 API Endpoints

- `GET /` - Home page
- `GET /images/upload/` - Upload form
- `POST /images/upload/` - Process image
- `GET /images/result/<id>/` - View processed image
- `GET /images/gallery/` - Browse all images
- `GET /images/download/<id>/` - Download image

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django framework
- Pillow for image processing
- Bootstrap for UI components
- AWS S3 for cloud storage
- Docker for containerization

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the deployment guide

---

**Built with ❤️ using Django, AWS S3, and Docker**
