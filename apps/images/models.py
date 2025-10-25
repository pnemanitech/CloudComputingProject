import uuid
from django.db import models
from apps.core.models import BaseModel


class ProcessedImage(BaseModel):
    """Model for storing processed images"""
    
    FILTER_CHOICES = [
        ('gray', 'Grayscale'),
        ('sepia', 'Sepia'),
        ('poster', 'Poster'),
        ('blur', 'Blur'),
        ('edge', 'Edge Detection'),
        ('solar', 'Solar'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_image = models.ImageField(upload_to='uploads/original/')
    processed_image = models.ImageField(upload_to='uploads/processed/', blank=True, null=True)
    filter_type = models.CharField(max_length=20, choices=FILTER_CHOICES)
    s3_url = models.URLField(blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Processed Image'
        verbose_name_plural = 'Processed Images'
    
    def __str__(self):
        return f"{self.get_filter_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
