import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class S3Manager:
    """AWS S3 utility class for uploading and managing images"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    def upload_image(self, file_path, s3_key):
        """Upload image to S3 bucket"""
        try:
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': 'image/jpeg'
                }
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
            return url
            
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return None
    
    def delete_image(self, s3_key):
        """Delete image from S3 bucket"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            logger.error(f"Error deleting from S3: {e}")
            return False
    
    def generate_s3_key(self, image_id, filter_type, file_extension='jpg'):
        """Generate S3 key for processed image"""
        return f"processed_images/{image_id}_{filter_type}.{file_extension}"
    
    def get_bucket_stats(self):
        """Get S3 bucket statistics"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return {
                'object_count': response.get('KeyCount', 0),
                'size_bytes': sum(obj.get('Size', 0) for obj in response.get('Contents', [])),
                'last_modified': max(
                    (obj.get('LastModified') for obj in response.get('Contents', [])),
                    default=None
                )
            }
        except ClientError as e:
            logger.error(f"Error getting bucket stats: {e}")
            return None
