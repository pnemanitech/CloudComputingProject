from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('s3/upload/', views.S3UploadView.as_view(), name='s3_upload'),
    path('s3/delete/', views.S3DeleteView.as_view(), name='s3_delete'),
    path('stats/', views.StorageStatsView.as_view(), name='stats'),
]
