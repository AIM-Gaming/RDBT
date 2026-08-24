from kivy.uix.image import Image
from PIL import Image as PILImage, ImageFilter


class BlurredImage(Image):
    def __init__(self, source, **kwargs):
        # Load and blur the image
        img = PILImage.open(source)
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Create a temporary path for the source
        blurred_path = "blurred_bg.jpg"
        img.save(blurred_path)
        
        # Initialize parent with the blurred image path
        super().__init__(source=blurred_path, **kwargs)
