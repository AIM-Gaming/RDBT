from assets import extract_video, extract_assets
from app import BibleTriviaApp

# Pressed pause button isn't the right size
# Update login and register pages (inputs are shoved down toward the buttons, pos_hint doesn't affect them)
# Debug game logic and visuals (check resume_game, reset, and home.py)
# Add api.py and integrate it
# Carousel centering is good enough for now, recalculate later

# Note: When the CarouselSelector's width is increased, it remains that way until the app is closed. Investigate later.

if __name__ == "__main__":
    extract_video()
    extract_assets()
    app = BibleTriviaApp()
    app.run()
