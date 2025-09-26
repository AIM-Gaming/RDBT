from assets import extract_video, extract_assets
from app import BibleTriviaApp

# Pressed pause button isn't the right size

# Just got my game back from the nearly 2-month old backup ;-;

if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()
