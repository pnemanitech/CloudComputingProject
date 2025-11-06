"""
Production settings for Image Processing Application.
"""
from .base import *
import dj_database_url
from socket import gethostbyname
from socket import gethostname

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS - handle comma-separated list and filter empty values
allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = ['*']  # Fallback to allow all hosts if not set

# Trust the X-Forwarded-Host header from the ALB
USE_X_FORWARDED_HOST = True

# Database
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    )
}

# Security settings for production
# Only enable HTTPS redirect if explicitly set (for HTTP Load Balancer, keep False)
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session security - only use secure cookies if using HTTPS
# For HTTP Load Balancer, set to False to allow cookies over HTTP
USE_HTTPS = os.environ.get('USE_HTTPS', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS

# CSRF trusted origins - allow Load Balancer domain
csrf_trusted_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_trusted_origins.split(',') if origin.strip()]
else:
    # Fallback: use ALLOWED_HOSTS to build trusted origins
    protocol = 'https' if USE_HTTPS else 'http'
    CSRF_TRUSTED_ORIGINS = [f'{protocol}://{host}' for host in ALLOWED_HOSTS if host != '*']

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# Static and Media files for production (use S3 if configured)
if os.environ.get('USE_S3_STORAGE', 'true').lower() == 'true' and os.environ.get('AWS_STORAGE_BUCKET_NAME'):
    # AWS S3 Configuration
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    # CRITICAL: Set to None to avoid ACL issues with S3 Block Public Access
    AWS_DEFAULT_ACL = None
    
    # S3 Storage Configuration
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_LOCATION = 'static'
    # Use IAM role for authentication (don't set ACCESS_KEY or SECRET_KEY)
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'virtual'
    AWS_QUERYSTRING_AUTH = False
    AWS_QUERYSTRING_EXPIRE = 3600  # URL expiration (not needed for public files)
    
    # Static files configuration for S3
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # Media files configuration for S3
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    # Use local static files with WhiteNoise (temporary fallback)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    STATIC_URL = '/static/'
    
    # Fallback to local storage
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Add WhiteNoise middleware after SecurityMiddleware
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Logging for production
LOGGING['handlers']['file']['filename'] = '/var/log/django/image_processing.log'
LOGGING['loggers']['django']['handlers'] = ['file', 'console']

# Add CloudWatch logging handler (optional - only if watchtower is installed)
# Set ENABLE_CLOUDWATCH_LOGS=true to enable CloudWatch logging
if os.environ.get('ENABLE_CLOUDWATCH_LOGS', 'false').lower() == 'true':
    try:
        import watchtower
        
        # Add CloudWatch handler
        cloudwatch_handler = {
            'level': 'INFO',
            'class': 'watchtower.CloudWatchLogHandler',
            'log_group': os.environ.get('CLOUDWATCH_LOG_GROUP', 'image-processing-django'),
            'stream_name': os.environ.get('CLOUDWATCH_LOG_STREAM', 'django-app'),
            'formatter': 'verbose',
            'use_queues': False,
            'create_log_group': True,
        }
        
        LOGGING['handlers']['cloudwatch'] = cloudwatch_handler
        
        # Add CloudWatch to handlers
        if 'loggers' in LOGGING and 'django' in LOGGING['loggers']:
            handlers = LOGGING['loggers']['django'].get('handlers', [])
            if isinstance(handlers, list):
                if 'cloudwatch' not in handlers:
                    handlers.append('cloudwatch')
                LOGGING['loggers']['django']['handlers'] = handlers
        
    except Exception as e:
        # CloudWatch logging failed, continue without it
        # Logs will still go to file and console
        pass
else:
    # CloudWatch logging disabled by default
    # Enable it by setting ENABLE_CLOUDWATCH_LOGS=true in environment
    pass


