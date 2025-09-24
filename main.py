from assets import extract_video, extract_assets
from app import BibleTriviaApp

# Pressed pause button isn't the right size

if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()
