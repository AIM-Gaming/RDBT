from kivy.uix.image import Image
from PIL import Image as PILImage, ImageFilter


class BlurredImage(Image):  # Makes image small
    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        
        # Load and blur the image
        img = PILImage.open(source)
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Create a temporary path for the source
        blurred_path = "blurred_bg.jpg"
        img.save(blurred_path)
        
        # Set the blurred image as the source
        self.source = blurred_path
