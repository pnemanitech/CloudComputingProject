from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('upload/', views.ImageUploadView.as_view(), name='upload'),
    path('result/<uuid:image_id>/', views.ImageResultView.as_view(), name='result'),
    path('download/<uuid:image_id>/', views.ImageDownloadView.as_view(), name='download'),
    path('gallery/', views.ImageGalleryView.as_view(), name='gallery'),
    path('process/', views.ProcessImageView.as_view(), name='process'),
]
