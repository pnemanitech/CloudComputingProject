from PIL import Image, ImageFilter, ImageOps
import numpy as np


class ImageProcessor:
    """Image processing class with various filter implementations"""
    
    @staticmethod
    def apply_grayscale(image):
        """Convert image to grayscale"""
        return image.convert('L')
    
    @staticmethod
    def apply_sepia(image):
        """Apply sepia filter to image"""
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Sepia matrix
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        
        # Apply sepia transformation using vectorized operations
        sepia_img = np.dot(img_array, sepia_matrix.T)
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        
        return Image.fromarray(sepia_img)
    
    @staticmethod
    def apply_poster(image):
        """Apply poster effect (reduce colors)"""
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Reduce colors by quantizing
        return image.quantize(colors=8).convert('RGB')
    
    @staticmethod
    def apply_blur(image):
        """Apply blur filter"""
        return image.filter(ImageFilter.BLUR)
    
    @staticmethod
    def apply_edge(image):
        """Apply edge detection filter"""
        # Convert to grayscale first
        if image.mode != 'L':
            image = image.convert('L')
        
        # Apply edge detection
        return image.filter(ImageFilter.FIND_EDGES)
    
    @staticmethod
    def apply_solar(image):
        """Apply solarization effect"""
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply solarization
        return ImageOps.solarize(image, threshold=128)
    
    @classmethod
    def process_image(cls, image, filter_type):
        """Process image with specified filter"""
        filter_methods = {
            'gray': cls.apply_grayscale,
            'sepia': cls.apply_sepia,
            'poster': cls.apply_poster,
            'blur': cls.apply_blur,
            'edge': cls.apply_edge,
            'solar': cls.apply_solar,
        }
        
        if filter_type not in filter_methods:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        return filter_methods[filter_type](image)
