from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils.s3_manager import S3Manager


class S3UploadView(LoginRequiredMixin, TemplateView):
    """View for S3 upload operations"""
    template_name = 'storage/s3_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'S3 Upload'
        return context


class S3DeleteView(LoginRequiredMixin, TemplateView):
    """View for S3 delete operations"""
    template_name = 'storage/s3_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'S3 Delete'
        return context


class StorageStatsView(LoginRequiredMixin, TemplateView):
    """View for storage statistics"""
    template_name = 'storage/stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Storage Statistics'
        
        # Get S3 stats if configured
        try:
            s3_manager = S3Manager()
            context['s3_stats'] = s3_manager.get_bucket_stats()
        except Exception as e:
            context['s3_error'] = str(e)
        
        return context
