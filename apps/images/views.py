from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from io import BytesIO  # ADD THIS LINE
import os
import tempfile
from PIL import Image
from .models import ProcessedImage
from .forms import ImageUploadForm
from apps.common.utils.image_filters import ImageProcessor
from apps.storage.utils.s3_manager import S3Manager


class ImageUploadView(FormView):
    """View for image upload form"""
    template_name = 'images/upload.html'
    form_class = ImageUploadForm
    success_url = '/images/result/'
    
    def form_valid(self, form):
        try:
            # Get form data
            uploaded_file = form.cleaned_data['original_image']
            filter_type = form.cleaned_data['filter_type']
            
            print(f"Processing image: {uploaded_file.name}, filter: {filter_type}")
            
            # CRITICAL: Read file content BEFORE saving to S3
            # Once saved to S3, the file object may be closed or unavailable
            uploaded_file.seek(0)  # Reset to beginning
            file_content = uploaded_file.read()
            file_size = len(file_content)
            uploaded_file.seek(0)  # Reset again for saving
            
            # Open image from the file content we just read
            original_img = Image.open(BytesIO(file_content))
            
            # Create ProcessedImage instance and save
            processed_image = ProcessedImage(
                original_image=uploaded_file,
                filter_type=filter_type
            )
            processed_image.save()
            
            print(f"Saved ProcessedImage with ID: {processed_image.id}")
            
            # Store image dimensions
            processed_image.width = original_img.width
            processed_image.height = original_img.height
            processed_image.file_size = file_size
            processed_image.save()
            
            # Apply filter
            filtered_img = ImageProcessor.process_image(original_img, filter_type)
            
            # Convert to RGB if necessary (JPEG doesn't support RGBA)
            if filtered_img.mode in ('RGBA', 'LA', 'P'):
                filtered_img = filtered_img.convert('RGB')
            
            # Save processed image temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                filtered_img.save(tmp_file.name, 'JPEG')
                tmp_path = tmp_file.name
            
            # Save processed image to model
            with open(tmp_path, 'rb') as f:
                processed_image.processed_image.save(
                    f'processed_{processed_image.id}_{filter_type}.jpg',
                    ContentFile(f.read()),
                    save=True
                )
            
            # Upload to S3 if configured (only if not already using S3 storage)
            # If using S3 storage backend, files are already uploaded to S3
            # Only need to get the URL if using local storage but want S3 URLs
            use_s3_storage = os.environ.get('USE_S3_STORAGE', 'true').lower() == 'true'
            if not use_s3_storage and (hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') and 
                settings.AWS_STORAGE_BUCKET_NAME and 
                settings.AWS_STORAGE_BUCKET_NAME != 'your-bucket-name-here'):
                
                try:
                    s3_manager = S3Manager()
                    s3_key = s3_manager.generate_s3_key(processed_image.id, filter_type)
                    # Try to get path, if not available (S3), use the file object
                    try:
                        processed_path = processed_image.processed_image.path
                    except (AttributeError, NotImplementedError):
                        # If using S3, file is already uploaded, just get the URL
                        processed_image.s3_url = processed_image.processed_image.url
                        processed_image.save()
                    else:
                        s3_url = s3_manager.upload_image(processed_path, s3_key)
                        if s3_url:
                            processed_image.s3_url = s3_url
                            processed_image.save()
                except Exception as e:
                    print(f"Warning: Could not upload to S3: {str(e)}")
                    # Continue without S3 URL
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            messages.success(self.request, 'Image processed successfully!')
            return redirect('images:result', image_id=processed_image.id)
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, f'Error processing image: {str(e)}')
            return redirect('images:upload')


class ImageResultView(TemplateView):
    """View for displaying processed image result"""
    template_name = 'images/result.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_id = self.kwargs['image_id']
        context['processed_image'] = get_object_or_404(ProcessedImage, id=image_id)
        return context


class ImageDownloadView(View):
    """View for downloading processed images"""
    
    def get(self, request, image_id):
        processed_image = get_object_or_404(ProcessedImage, id=image_id)
        
        if processed_image.processed_image:
            response = HttpResponse(
                processed_image.processed_image.read(),
                content_type='image/jpeg'
            )
            response['Content-Disposition'] = f'attachment; filename="processed_{processed_image.filter_type}_{image_id}.jpg"'
            return response
        else:
            messages.error(request, 'Processed image not found.')
            return redirect('core:home')


class ImageGalleryView(TemplateView):
    """View for displaying image gallery"""
    template_name = 'images/gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['processed_images'] = ProcessedImage.objects.all()
        return context


class ProcessImageView(View):
    """API view for processing images via AJAX"""
    
    def post(self, request):
        # This can be used for AJAX processing
        pass
