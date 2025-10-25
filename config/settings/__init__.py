"""
Settings package for Image Processing Application.
"""

import os

# Determine which settings to use based on environment
ENVIRONMENT = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if ENVIRONMENT == 'config.settings.production':
    from .production import *
else:
    from .development import *
