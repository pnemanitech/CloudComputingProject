from django import forms
from .models import ProcessedImage


class ImageUploadForm(forms.ModelForm):
    """Form for image upload and processing"""
    
    class Meta:
        model = ProcessedImage
        fields = ['original_image', 'filter_type']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'imageInput'
            }),
            'filter_type': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }, choices=ProcessedImage.FILTER_CHOICES)
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original_image'].required = True
        self.fields['filter_type'].required = True
        # Remove empty choice from filter_type field
        self.fields['filter_type'].empty_label = None
