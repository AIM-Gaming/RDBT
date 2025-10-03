from assets import extract_video, extract_assets
from app import BibleTriviaApp

# Pressed pause button isn't the right size
# Adjust carousel selector

# Note: When the CarouselSelector's width is increased, it remains that way until the app is closed. Investigate later.

if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()
